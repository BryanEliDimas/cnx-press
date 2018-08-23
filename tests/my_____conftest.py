import hashlib
import io
import os
import pathlib
import random
import shutil
import tempfile
import warnings
import zipfile
from copy import copy, deepcopy

import jinja2
import pretend
import pytest
from cnxdb.init import init_db
from litezip import Collection, Module
from litezip.main import COLLECTION_NSMAP
from lxml import etree
from pyramid import testing as pyramid_testing
from pyramid.request import apply_request_extensions, Request
from pyramid.settings import asbool
from recordclass import recordclass
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.sql import select, text

from .helpers import element_tree_from_model


TEMPLATE_DIR = pathlib.Path(__file__).parent / '_templates'
with (TEMPLATE_DIR / 'module.xml').open('r') as fb:
    MODULE_DOC = fb.read()
with (TEMPLATE_DIR / 'collection.xml').open('r') as fb:
    COLLECTION_DOC = fb.read()


def _maybe_set(env_var, value):
    """Only set the env_var if it doesn't already contain a value."""
    os.environ.setdefault(env_var, value)
    return os.environ[env_var]


PERSONS = (
    # personid, firstname, surname, fullname, email
    ['user1', 'User', 'One', 'User One', 'user1@example.com'],
    ['user2', 'User', 'Two', 'User Duo', 'user2@example.com'],
    ['user3', 'User', 'Three', 'Usuario Tres', 'user3@example.com'],
    ['user4', 'User', 'Four', 'User IIII', 'user4@example.com'],
)


SUBJECTS = (
    'Arts',
    'Business',
    'Humanities',
    'Mathematics and Statistics',
    'Science and Technology',
    'Social Sciences',
)


# Hard coded here because there is not a method for inputting this value.
GOOGLE_ANALYTICS_CODE = 'abc123'

@pytest.fixture(scope='session', autouse=True)
def testing(_init_database, db_engines, db_tables_session_scope):
    """This fixture clears all the tables prior to any test run.
    Additionally, it minimally sets up database content. This content
    is of the type that would not typically be handed by this application.

    """
    tables = (
        'trees',
        'modulecounts',
        'modulekeywords',
        'similarities',
        'modulefti',
        'module_files',
        'collated_fti',
        'moduletags',
        'moduleoptionalroles',
        'moduleratings',
        'document_baking_result_associations',
        'collated_file_associations',
        'modules',
        'latest_modules',
        'abstracts',
        'keywords',
        'files',
        'users',
        'overall_hit_ranks',
        'recent_hit_ranks',
        'persons',
        'print_style_recipes',
        'default_print_style_recipes',
        'document_hits',
        'service_state_messages',
        'publications',
        'role_acceptances',
        'license_acceptances',
        'document_acl',
        'pending_resource_associations',
        'pending_documents',
        'pending_resources',
        'api_keys',
        'document_controls',
    )
    # Clear out the tables
    t = db_tables_session_scope
    for table in tables:
        stmt = getattr(t, table).delete()
        db_engines['common'].execute(stmt)

    # Insert 'persons', because this application doesn't do people.
    # You either have a user before publishing or some other means of
    # creating a user exists.
    column_names = ['personid', 'firstname', 'surname', 'fullname', 'email']
    db_engines['common'].execute(
        t.persons.insert(),
        [dict(zip(column_names, x)) for x in PERSONS])


# ###
#  Collection Tree models
# ###
SubCollection = recordclass('SubCollection',  # aka Tree Container
                            'title contents')
ModuleNode = recordclass('ModuleNode',  # aka Tree Node
                         'title id version version_at module')


# ###
#  Content Utility
# ###
class _ContentUtil:

    _word_catalog_filepath = '/usr/share/dict/words'
    _persons = PERSONS
    _subjects = SUBJECTS

    Module = Module
    Collection = Collection
    Resource = None

    def __init__(self):
        with open(self._word_catalog_filepath, 'r') as fb:
            word_catalog = list([x for x in fb.read().splitlines()
                                 if len(x) >= 3 and "'" not in x])
        self.word_catalog = word_catalog
        self._created_dirs = []
        # Import during singleton creation
        from press.models import Resource
        self.Resource = Resource

    def _clean_up(self):
        for dir in self._created_dirs[::-1]:
            shutil.rmtree(str(dir))

    def _mkdir(self, start_at=None):
        if start_at is None:
            dir = pathlib.Path(tempfile.mkdtemp())
        else:
            dirnames = tempfile._get_candidate_names()
            while True:
                dir = start_at / next(dirnames)
                try:
                    dir.mkdir()
                except FileExistsError:
                    continue
                break
        self._created_dirs.append(dir)
        return dir

    def _gen_dir(self, relative_to=None):
        dir = None
        if isinstance(relative_to, pathlib.Path):
            path = relative_to
            dir = path.is_file() and path.parent or path
        elif isinstance(relative_to, Module):
            dir = relative_to.file.parent.parent
        elif isinstance(relative_to, Collection):
            dir = relative_to.file.parent
        return self._mkdir(start_at=dir)

    def _rand_id_num(self):
        return random.randint(10000, 99999)

    def _parse_module_metadata(self, *args, **kwargs):
        # The parser is validly used here because it is unit tested
        # without using this utility.
        from press.parsers import parse_module_metadata
        return parse_module_metadata(*args, **kwargs)

    def _parse_collection_metadata(self, *args, **kwargs):
        # The parser is validly used here because it is unit tested
        # without using this utility.
        from press.parsers import parse_collection_metadata
        return parse_collection_metadata(*args, **kwargs)

    def randid(self, prefix='m'):
        return '{}{}'.format(prefix, self._rand_id_num())

    def randword(self):
        return random.choice(self.word_catalog)

    def randtitle(self):
        return ' '.join([self.randword(),
                         self.randword(),
                         self.randword()])

    def randperson(self):
        return random.choice(self._persons)

    def randsubj(self):
        return random.choice(self._subjects)

    def rand_module_id(self):
        return 'm{}'.format(self._rand_id_num)

    def copy_model(self, model, relative_to=None):
        """Copy the given model"""
        # This is mostly useful, because a copy of the object isn't enough
        # since much of the model's data is on the filesystem.

        model_type = type(model)
        new_model_dir = self._gen_dir(relative_to=relative_to)
        filename = {
            self.Collection: 'collection.xml',
            self.Module: 'index.cnxml',
        }[model_type]
        new_model_filepath = new_model_dir / filename

        # Copy content
        with new_model_filepath.open('w') as fb, model.file.open('r') as o:
            fb.write(o.read())
        # Copy resources
        new_resources = deepcopy(model.resources)

        return model_type(
            model.id,
            pathlib.Path(new_model_filepath),
            new_resources,
        )

# bryan - just a lil interesting.
    def gen_module_metadata(self, id=None, derived_from_metadata=None):
        return {
            'id': id,
            'version': '1.1',
            'created': '2010/12/15 10:58:00 -0600',
            'revised': '2011/08/16 13:55:25 -0500',
            'title': self.randtitle(),
            'license_url': 'http://creativecommons.org/licenses/by-nc-sa/4.0/',
            'language': 'en',
            'print_style': self.randword(),
            'authors': set([self.randperson()[0],
                            self.randperson()[0]]),
            'maintainers': set([self.randperson()[0],
                                self.randperson()[0]]),
            'licensors': [self.randperson()[0]],
            'keywords': [self.randword()
                         for x in range(1, random.randint(1, 5))],
            'subjects': [self.randsubj()],
            'abstract': self.randtitle(),
            'derived_from': derived_from_metadata,
        }

    def gen_cnxml(self, metadata, resources, terms=[]):
        template = jinja2.Template(MODULE_DOC)
        return template.render(metadata=metadata, resources=resources,
                               terms=' '.join(terms))

# bryan - this is parsing colxml, or rendering, rather, to generate colxml.
    def gen_colxml(self, metadata, tree):
        template = jinja2.Template(COLLECTION_DOC)
        return template.render(metadata=metadata, tree=tree)

    def gen_resource(self):
        content = io.StringIO(' '.join([self.randtitle(), self.randtitle()]))
        filename = '_'.join([self.randword(), self.randword()]) + '.txt'

        hasher = hashlib.sha1()
        hasher.update(content.read().encode('utf-8'))
        sha1 = hasher.hexdigest()
        content.seek(0)

        return self.Resource(
            content,
            filename,
            'text/plain',
            sha1,
        )

    def gen_module(self, id=None, resources=[], relative_to=None,
                   derived_from=None):
        id = not id and self.randid(prefix='m') or id
        module_dir = self._gen_dir(relative_to=relative_to)
        module_filepath = module_dir / 'index.cnxml'

        # Generate metadata
        if derived_from:
            derived_metadata = self._parse_collection_metadata(derived_from)
        else:
            derived_metadata = None
        metadata = self.gen_module_metadata(
            id=id,
            derived_from_metadata=derived_metadata,
        )

        with module_filepath.open('w') as fb:
            fb.write(self.gen_cnxml(metadata, resources))
        return self.Module(id, pathlib.Path(module_filepath), resources)

# bryan
    def gen_collection(self, id=None, modules=[], resources=[],
                       relative_to=None, derived_from=None):
        id = not id and self.randid(prefix='col') or id
        relative_to = dir = self._gen_dir(relative_to=relative_to)
        filepath = dir / 'collection.xml'

        # Generate metadata
        if derived_from:
            derived_metadata = self._parse_collection_metadata(derived_from)
        else:
            derived_metadata = None
        metadata = self.gen_module_metadata(
            id=id,
            derived_from_metadata=derived_metadata,
        )

        # Generate the tree
        tree, modules = self.gen_collection_tree(
            modules=modules,
            relative_to=relative_to,
        )

        # Write the colxml to the filesystem
        with filepath.open('w') as fb:
            fb.write(self.gen_colxml(metadata, tree))
        collection = self.Collection(id, pathlib.Path(filepath), resources)

        return collection, tree, modules

    def gen_collection_objects_tree(self, modules=[],
                                    max_depth=1, depth=0, relative_to=None):
        pass


# bryan - my assignment is to replace this function, pretty much.
    def gen_collection_tree(self, modules=[],
                            max_depth=1, depth=0, relative_to=None):
        """Returns a sequence containing a dict of title and contents
        and/or Module objects.

        """
        tree = []
        for module in modules:
            node = self.make_tree_node_from(module)
            tree.append(node)
        for x in range(2, 6):
            if random.randint(1, 40) % 2 == 0 or depth == max_depth:
                module = self.gen_module(relative_to=relative_to)
                modules.append(module)
                node = self.make_tree_node_from(module)
                tree.append(node)
            else:
                contents, additional_modules = self.gen_collection_tree(
                    max_depth=max_depth,
                    depth=depth + 1,
                    relative_to=relative_to)
                modules.extend(additional_modules)
                sub_col = SubCollection(title=self.randtitle(),
                                        contents=contents)
                tree.append(sub_col)
        return tree, modules

    def make_tree_node_from(self, module):
        metadata = self._parse_module_metadata(module)
        node = ModuleNode(id=metadata.id,
                          version='latest',
                          version_at=metadata.version,
                          title=metadata.title,
                          module=module)
        return node


@pytest.fixture(scope='session')
def content_util(request):
    util = _ContentUtil()
    request.addfinalizer(util._clean_up)
    return util
