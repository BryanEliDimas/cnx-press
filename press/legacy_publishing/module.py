from pyramid.threadlocal import get_current_request
from sqlalchemy.sql import text

from .utils import replace_id_and_version
from ..errors import StaleVersion

__all__ = (
    'publish_legacy_page',
)


def publish_legacy_page(model, metadata, submission, db_conn):
    """Publish a Page (aka Module) as the legacy (zope-based) system
    would.

    :param model: module
    :type model: :class:`litezip.Module`
    :type metadata: :class:`press.models.ModuleMetadata`
    :param submission: a two value tuple containing a userid
                       and submit message
    :type submission: tuple
    :param db_conn: a database connection object
    :type db_conn: :class:`sqlalchemy.engine.Connection`

    """
    t = get_current_request().db_tables

    if model.id is None or metadata.id is None:  # pragma: no cover
        raise NotImplementedError()

    result = db_conn.execute(
        t.latest_modules.select()
        .where(t.latest_modules.c.moduleid == metadata.id)
    )
    # At this time, this code assumes an existing module
    existing_module = result.fetchone()

    if metadata.version != existing_module.version:
        raise StaleVersion(metadata.version, existing_module.version, model)

    major_version = existing_module.major_version + 1

    # Get existing abstract, if exists, otherwise add it
    result = db_conn.execute(
        t.abstracts.select()
        .where(t.abstracts.c.abstract == metadata.abstract)
    )
    try:
        abstractid = result.fetchone().abstractid
    except AttributeError:  # NoneType
        result = db_conn.execute(t.abstracts.insert()
                                 .values(abstract=metadata.abstract))
        abstractid = result.inserted_primary_key[0]

    # Get the license identifier
    result = db_conn.execute(
        t.licenses.select()
        .where(t.licenses.c.url == metadata.license_url))
    licenseid = result.fetchone().licenseid

    # Insert module metadata
    result = db_conn.execute(t.modules.insert().values(
        uuid=existing_module.uuid,
        moduleid=metadata.id,
        major_version=major_version,
        portal_type='Module',
        name=metadata.title,
        created=existing_module.created,
        abstractid=abstractid,
        licenseid=licenseid,
        doctype='',
        submitter=submission[0],
        submitlog=submission[1],
        language=metadata.language,
        authors=metadata.authors,
        maintainers=metadata.maintainers,
        licensors=metadata.licensors,
        # Carry over parentage information
        parent=existing_module.parent,
        parentauthors=existing_module.parentauthors,
        google_analytics=existing_module.google_analytics,
    ).returning(
        t.modules.c.module_ident,
        t.modules.c.moduleid,
        t.modules.c.major_version,
        t.modules.c.minor_version,
    ))
    ident, id, major_version, minor_version = result.fetchone()
    version = (major_version, minor_version,)

    # Insert subjects metadata
    stmt = (text('INSERT INTO moduletags '
                 'SELECT :module_ident AS module_ident, tagid '
                 'FROM tags WHERE tag = any(:subjects)')
            .bindparams(module_ident=ident,
                        subjects=list(metadata.subjects)))
    result = db_conn.execute(stmt)

    # Insert keywords metadata
    stmt = (text('INSERT INTO keywords (word) '
                 'SELECT iword AS word '
                 'FROM unnest(:keywords ::text[]) AS iword '
                 '     LEFT JOIN keywords AS kw ON (kw.word = iword) '
                 'WHERE kw.keywordid IS NULL')
            .bindparams(keywords=list(metadata.keywords)))
    db_conn.execute(stmt)
    stmt = (text('INSERT INTO modulekeywords '
                 'SELECT :module_ident AS module_ident, keywordid '
                 'FROM keywords WHERE word = any(:keywords)')
            .bindparams(module_ident=ident,
                        keywords=list(metadata.keywords)))
    db_conn.execute(stmt)

    # Insert resource files (images, pdfs, etc.)
    for resource in model.resources:
        try:
            # Try finding an existing file first
            fileid = db_conn.execute(
                text('SELECT fileid FROM '
                     'files WHERE sha1 = :sha1')
                .bindparams(sha1=resource.sha1)
            ).fetchone().fileid
        except AttributeError:
            # Insert it when it doesn't exist
            result = db_conn.execute(
                t.files.insert().values(
                    file=resource.data.read(),
                    media_type=resource.media_type,
                )
            )
            resource.data.seek(0)
            fileid = result.inserted_primary_key[0]
        result = db_conn.execute(
            t.module_files.insert().values(
                module_ident=ident,
                fileid=fileid,
                filename=resource.filename,
            )
        )

    # Copy over existing module_files entries
    stmt = text(
        'INSERT INTO module_files '
        'SELECT :module_ident, fileid, filename '
        'FROM module_files '
        'WHERE module_ident = :previous_module_ident '
        '      AND ('
        '          filename NOT IN (SELECT filename '
        '                           FROM module_files '
        '                           WHERE module_ident = :module_ident)'
        '          AND filename !~ \'index.cnxml\')'
    )
    db_conn.execute(
        stmt,
        module_ident=ident,
        previous_module_ident=existing_module.module_ident,
    )

    # Rewrite the content with the id and version
    replace_id_and_version(model, id, version)

    # Insert module files (content and resources)
    with model.file.open('rb') as fb:
        result = db_conn.execute(t.files.insert().values(
            file=fb.read(),
            media_type='text/xml',
        ))
    fileid = result.inserted_primary_key[0]
    result = db_conn.execute(t.module_files.insert().values(
        module_ident=ident,
        fileid=fileid,
        filename='index.cnxml',
    ))

    return (id, version), ident
