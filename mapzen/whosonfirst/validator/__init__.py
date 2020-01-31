import sys
import os.path
import logging
import json
import geojson

import mapzen.whosonfirst.export
import mapzen.whosonfirst.placetypes
import mapzen.whosonfirst.sources
import mapzen.whosonfirst.utils

class reporter:

    def __init__(self):

        self._debug_ = []
        self._info_ = []
        self._warning_ = []
        self._error_ = []

    def __repr__(self):
        return str(self.ok())

    def report(self):

        return {
            'debug': self._debug_,
            'info': self._info_,
            'warning': self._warning_,
            'error': self._error_,
            'ok': self.ok()
        }

    def print_report(self, fh=sys.stdout):

        report = self.report()

        for k, details in report.items():
            fh.write("# %s\n\n" % k)

            if type(details) == list:

                if len(details) > 0:

                    for ln in details:
                        fh.write("* %s\n" % ln)

                    fh.write("\n")

            else:
                fh.write("* %s\n\n" % (str(details)))


    def ok(self, strict=False):

        ok = True

        if strict:
            if len(self._warning_):
                ok = False
        else:
            if len(self._error_):
                ok = False

        return ok

    def debug(self, msg):
        self._debug_.append(msg)
        logging.debug(msg)

    def info(self, msg):
        self._info_.append(msg)
        logging.info(msg)

    def warning(self, msg):
        self._warning_.append(msg)
        logging.debug(msg)

    def error(self, msg):
        self._error_.append(msg)
        logging.error(msg)

class validator:

    def __init__(self, **kwargs):

        self.do_derive = kwargs.get('derive', False)
        self.exporter = kwargs.get('exporter', None)

        self._path_ = "feature"

        self._required_ = {
            'wof:id': int,
            'wof:parent_id': int,
            'wof:name': str,
            'wof:placetype': str,
            'wof:country': str,
            'wof:concordances': dict,
            'wof:hierarchy': list,
            'wof:belongsto': list,
            'wof:supersedes': list,
            'wof:superseded_by': list,
            'wof:breaches': list,
            'wof:tags': list,
            'iso:country': str,
            'src:geom': str,
            'edtf:inception': str,
            'edtf:cessation': str,
            # 'geom:area': types.FloatType,
            # 'geom:latitude': types.FloatType,
            # 'geom:longitude': types.FloatType,
        }

        self._defaults_ = {
            'edtf:cessation': "uuuu",
            'edtf:inception': "uuuu",
            'wof:belongsto': [],
            'wof:country': "",
            'wof:concordances': {},
            'wof:hierarchy': [],
            'wof:parent_id': -1,
            'wof:superseded_by': [],
            'wof:supersedes': [],
            'wof:tags': [],
        }

    def required_attributes(self):

        for k, v in self._required_.items():
            yield k, v

    def default_value(self, prop):

        return self._defaults_.get(prop, None)

    def validate_file(self, path):

        self._path_ = path
        logging.debug("process %s" % self._path_)

        try:
            fh = open(path, 'r')
            feature = geojson.load(fh)
        except Exception as e:

            r = reporter()
            r.error("failed to open %s because %s" % (self._path_, e))
            return r

        return self.validate_feature(feature)

    def validate_feature(self, feature):

        r = reporter()

        updated = False

        isa = feature.get('type', None)

        # The absence of this will cause whatever GeoJSON parser things
        # like GitHub and Mapshaper use to cry like a baby. On the other
        # hand py-geojson will happily just work. Because everyone is
        # doomed to reimplement XML Schema sooner or later...
        # (20150831/thisisaaronland)

        if isa != 'Feature':
            r.error("%s has an invalid type: %s" % (self._path_, isa))

            feature['type'] = 'Feature'
            updated = True

        props = feature['properties']

        # ensure keys

        for k, ignore in self.required_attributes():

            # r.info("look for %s" % k)

            if k in props:
                r.debug("%s has key (%s)" % (self._path_, k))
                continue

            r.warning("%s is missing key %s" % (self._path_, k))

            default = self.default_value(k)

            if default:
                r.debug("assign default value (%s) to %s" % (default, k))
                props[k] = default
                updated = True

        # ensure expected types (for values)

        for k, expected in self.required_attributes():

            v = props.get(k, None)
            isa = type(v)

            if isa == expected:
                r.debug("%s has key (%s) with expected value (%s)" % (self._path_, k, isa))
                continue

            r.warning("%s has incorrect value for %s, expected %s but got %s (%s)" % (self._path_, k, expected, isa, v))

            if k == 'wof:hierarchy':

                if isa == dict:
                    props['wof:hierarchy'] = [v]
                    updated = True

            elif k == 'wof:parent_id':

                if isa == type(None):
                    props['wof:parent_id'] = -1
                    updated = True

                elif isa == str:
                    props['wof:parent_id'] = int(v)
                    updated = True

                else:
                    pass

            elif k == 'src:geom':

                # Note - this will trigger a warning below
                # (20151215/thisisaaronland)

                if isa == type(None):
                    props['src:geom'] = "unknown"
                    updated = True
                else:
                    pass

            elif k == 'iso:country':

                if isa == bytes:
                    props['iso:country'] = str(v)
                    updated = True
                else:
                    pass

            elif k == 'wof:country':

                if isa == bytes:
                    props['wof:country'] = str(v)
                    updated = True
                else:
                    pass

            # see also: https://github.com/whosonfirst/py-mapzen-whosonfirst-validator/issues/2

            elif k == 'edtf:inception':

                if isa == bytes:
                    props['edtf:inception'] = str(v)
                    updated = True
                else:
                    pass

            elif k == 'edtf:cessation':

                if isa == bytes:
                    props['edtf:cessation'] = str(v)
                    updated = True
                else:
                    pass

            else:
                pass

        # try to derive values from existing data or services - not certain this should
        # even stay here... (20150925/thisisaaronland)

        if self.do_derive:

            hier = props.get('wof:hierarchy', [])
            count_hiers = len(hier)

            if 0 and count_hiers == 0:

                hier = mapzen.whosonfirst.utils.generate_hierarchy(feature)
                count_hiers = len(hier)

                if count_hiers == 0:
                    r.warning("%s has a zero length hierarchy but unable to figure it out" % self._path_)
                else:
                    r.info("%s had a zero length hierarchy and now it doesn't" % self._path_)
                    props['wof:hierarchy'] = hier
                    updated = True

            if not props.get('src:geom', False) and props.get('geom:source', False):
                r.info("%s has missing 'src:geom' that can be derived by 'geom:source'" % self._path_)
                props['src:geom'] = props['geom:source']
                del(props['geom:source'])
                updated = True

            # TO DO - ensure that are the IDs are ints (and not strings)
            # (20150819/thisisaaronland)

            # check parent_id

            parent_id = props.get('wof:parent_id', -1)

            if parent_id == -1:

                if count_hiers == 1:

                    placetype = props['wof:placetype']
                    placetype = mapzen.whosonfirst.placetypes.placetype(placetype)

                    new_parent_id = None

                    # sudo make me recurse up through ancestors?

                    for pt in placetype.parents():

                        parent_id_key = "%s_id" % pt
                        new_parent_id = hier[0].get(parent_id_key, None)

                        if new_parent_id:
                            break

                        if new_parent_id and new_parent_id != -1:
                            r.info("%s has -1 parent id and setting to %s" % (self._path_, new_parent_id))
                            props['wof:parent_id'] = new_parent_id
                            updated = True

                        else:
                            r.warning("%s has no parent and a single hierarchy but unable to figure it out..." % self._path_)

                elif count_hiers:
                    r.info("%s has multiple hiers so no easy way to determine parent" % self._path_)
                else:
                    pass

        # end of try to derive stuff

        # check src:geom

        src = props['src:geom']

        if not mapzen.whosonfirst.sources.is_valid_source(src):
            r.warning("unknown or invalid src:geom")

        # check wof:name

        name = props.get("wof:name", "")

        if not name or len(name) == 0:
            r.warning("%s has a zero-length (or null) name" % self._path_)

        # check ISO country

        iso = props.get("iso:country", "")

        if len(iso) != 2:
            r.warning("%s has a weird ISO" % self._path_)

        if updated:

            if self.exporter:

                r.info("%s has changes that will be written to disk" % self._path_)
                feature['properties'] = props
                self.exporter.export_feature(feature)
            else:
                r.debug("%s has changed but no exporter has been defined so updates will not apply" % self._path_)

        return r

if __name__ == '__main__':

    import sys
    import os.path

    vld = validator()

    for path in sys.argv[1:] :

        path = os.path.abspath(path)
        rptr = vld.validate_file(path)

        print("%s : %s" % (path, rptr.ok()))
        print(rptr.print_report())
