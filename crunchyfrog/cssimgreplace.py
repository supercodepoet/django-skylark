"""
From the W3 Spec

URI values (Uniform Resource Identifiers, see [RFC3986], which includes URLs,
URNs, etc) in this specification are denoted by <uri>. The functional notation
used to designate URIs in property values is "url()", as in:

    Example(s):

        body { background: url("http://www.example.com/pinkish.png") }

    The format of a URI value is 'url(' followed by optional white space
    followed by an optional single quote (') or double quote (") character
    followed by the URI itself, followed by an optional single quote (') or
    double quote (") character followed by optional white space followed by
    ')'. The two quote characters must be the same.

Example(s):

    An example without quotes:

        li { list-style: url(http://www.example.com/redball.png) disc }

    Some characters appearing in an unquoted URI, such as parentheses, commas,
    white space characters, single quotes (') and double quotes ("), must be
    escaped with a backslash so that the resulting URI value is a URI token:
        '\(', '\)', '\,'.

    Depending on the type of URI, it might also be possible to write the above
    characters as URI-escapes (where "(" = %28, ")" = %29, etc.) as described
    in [RFC3986].

    In order to create modular style sheets that are not dependent on the
    absolute location of a resource, authors may use relative URIs. Relative
    URIs (as defined in [RFC3986]) are resolved to full URIs using a base URI.
    RFC 3986, section 5, defines the normative algorithm for this process. For
    CSS style sheets, the base URI is that of the style sheet, not that of the
    source document. 
"""
import re
from os.path import normpath

#[\"'\(\)]
url_value_re = re.compile(r"""
   url\(
       (\"|')?
        \s*
        ((
            [^\"'\(\)]|(?<=\\)
        )*)
        \s*
        (\"|')?
    \)
      """, re.VERBOSE)


def relative_replace(source, css_path, cache_base_url):
    urls_replaced = []   # List of urls we've already replaced so we can skip
    replacement = source
    for match in url_value_re.finditer(source):
        url_value = match.group()
        if url_value in urls_replaced:
            # We've already replaced this one
            continue
        urls_replaced.append(url_value)
        
        # The url under question
        url = match.group(2)

        if url.startswith('http') or url.startswith('https') or \
           url.startswith('/'):
            # We need to leave this sucker alone, it's not the droids that we
            # are looking for.  It's either an absolute url or 
            # fully-qualified.
            continue

        full_path = normpath('/'.join((css_path, url,)))
        new_url_value = '%s%s' % (cache_base_url, full_path)

        # We are going to borrow os.path.normpath to fix any double slashes or
        # any ../ parts
        replacement = replacement.replace(url_value,
            'url(%s%s%s)' % (match.group(1) or '', new_url_value,
                             match.group(4) or ''))

    return replacement
