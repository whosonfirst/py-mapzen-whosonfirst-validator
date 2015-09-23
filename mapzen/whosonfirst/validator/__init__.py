# https://pythonhosted.org/setuptools/setuptools.html#namespace-packages
__import__('pkg_resources').declare_namespace(__name__)

import sys
import os.path
import logging
import json
import geojson
import types

import mapzen.whosonfirst.utils
import mapzen.whosonfirst.export
import mapzen.whosonfirst.placetypes

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
        logging.warning(msg)

    def error(self, msg):
        self._error_.append(msg)
        logging.error(msg)

class validator:

    def __init__(self, **kwargs):

        self.do_update = kwargs.get('update', False)
        self.do_export = kwargs.get('export', False)
        self.do_derive = kwargs.get('derive', False)

    def validate_file(self, path):
    
        logging.debug("process %s" % path)

        try:
            fh = open(path, 'r')
            feature = geojson.load(fh)
        except Exception, e:

            r = reporter()
            r.error("failed to open %s because %s" % (path, e))
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
            r.error("%s has an invalid type: %s" % (path, isa))

            feature['type'] = 'Feature'

            if self.do_update:
                exporter.export_feature(feature)

        props = feature['properties']

        required = {
            'wof:id': types.IntType,
            'wof:parent_id': types.IntType,
            'wof:name': types.UnicodeType,
            'wof:placetype': types.UnicodeType,
            'wof:country': types.UnicodeType,
            'wof:concordances': types.DictType,
            'wof:hierarchy': types.ListType,
            'wof:belongsto': types.ListType,
            'wof:supersedes': types.ListType,
            'wof:superseded_by': types.ListType,
            'wof:breaches': types.ListType,
            'wof:tags': types.ListType,
            'iso:country': types.UnicodeType,
            'src:geom': types.UnicodeType,
            'edtf:inception': types.UnicodeType,
            'edtf:cessation': types.UnicodeType,
            # 'geom:area': types.FloatType,
            # 'geom:latitude': types.FloatType,
            # 'geom:longitude': types.FloatType,
        }
        
        # ensure keys
    
        for k, ignore in required.items():

            # r.info("look for %s" % k)
            
            if props.has_key(k):
                r.debug("%s has key (%s)" % ("feature", k))
                continue
            
            r.warning("%s is missing key %s" % ("feature", k))

            updated = False

            if k == 'wof:parent_id':
                r.info("assigning parent_id as -1")
                props['wof:parent_id'] = -1
                updated = True
                
            elif k == 'iso:country':
                r.info("assigning empty iso:country")
                props['iso:country'] = ""
                updated = True
                
            elif k == 'wof:country':
                r.info("assigning empty wof:country")
                props['wof:country'] = ""
                updated = True
                
            elif k == 'wof:concordances':
                r.info("assigning empty concordances")
                props['wof:concordances'] = {}
                updated = True
                
            elif k == 'wof:hierarchy':
                r.info("assigning empty hierarchy")
                props['wof:hierarchy'] = [] 
                updated = True
                
            elif k == 'wof:belongsto':
                r.info("assigning empty belongsto")
                props['wof:belongsto'] = [] 
                updated = True
                
            elif k == 'wof:supersedes':
                r.info("assigning empty supersedes")
                props['wof:supersedes'] = [] 
                updated = True
                
            elif k == 'wof:superseded_by':
                r.info("assigning empty superseded_by")
                props['wof:superseded_by'] = [] 
                updated = True
                
            elif k == 'wof:tags': 
                r.info("assigning empty tags")
                props['wof:tags'] = [] 
                updated = True
                
            elif k == 'edtf:inception':
                r.info("assigning empty inception date")
                props['edtf:inception'] = u"u"
                updated = True
                
            elif k == 'edtf:cessation':
                r.info("assigning empty cessation date")
                props['edtf:cessation'] = u"u"
                updated = True
                
            else:
                pass
            
            if updated and self.do_update:
                feature['properties'] = props
                # exporter.export_feature(feature)

        # ensure expected types (for values)

        for k, expected in required.items():
        
            v = props.get(k, None)
            isa = type(v)
        
            if isa == expected:
                r.debug("%s has key (%s) with expected value (%s)" % ("feature", k, isa))
                continue
            
            r.warning("%s has incorrect value for %s, expected %s but got %s (%s)" % ("feature", k, expected, isa, v))

            updated = False

            if k == 'wof:hierarchy':
                
                if isa == types.DictType:
                    props['wof:hierarchy'] = [v]
                    updated = True
                
            elif k == 'wof:parent_id':
                
                if isa == types.NoneType:
                    props['wof:parent_id'] = -1
                    updated = True
                    
                elif isa == types.UnicodeType:
                    props['wof:parent_id'] = int(v)
                    updated = True
                    
                else:
                    pass
            
            elif k == 'src:geom':

                if isa == types.NoneType:
                    props['src:geom'] = "unknown"
                    updated = True
                else:
                    pass

            elif k == 'iso:country':
                    
                if isa == types.StringType:
                    props['iso:country'] = unicode(v)
                    updated = True
                else:
                    pass

            elif k == 'wof:country':
                    
                if isa == types.StringType:
                    props['wof:country'] = unicode(v)
                    updated = True
                else:
                    pass

            elif k == 'edtf:inception':
                    
                if isa == types.StringType:
                    props['edtf:inception'] = unicode(v)
                    updated = True
                else:
                    pass

            elif k == 'edtf:cessation':
                    
                if isa == types.StringType:
                    props['edtf:cessation'] = unicode(v)
                    updated = True
                else:
                    pass

            else:
                pass

        if updated and self.do_update:
            feature['properties'] = props
            exporter.export_feature(feature)
            
        if not self.do_derive:
            return r
    
        # try to derive values from existing data or services
        
        updated = False
        
        hier = props.get('wof:hierarchy', [])
        count_hiers = len(hier)

        if 0 and count_hiers == 0:
    
            hier = mapzen.whosonfirst.utils.generate_hierarchy(feature)
            count_hiers = len(hier)
            
            if count_hiers == 0:
                r.warning("%s has a zero length hierarchy but unable to figure it out" % "feature")
            else:
                r.info("%s had a zero length hierarchy and now it doesn't" % "feature")
                props['wof:hierarchy'] = hier
                updated = True

        if not props.get('src:geom', False) and props.get('geom:source', False):
            r.info("%s has missing 'src:geom' that can be derived by 'geom:source'" % "feature")
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
                    r.info("%s has -1 parent id and setting to %s" % ("feature", new_parent_id))
                    props['wof:parent_id'] = new_parent_id
                    updated = True

                else:
                    r.warning("%s has no parent and a single hierarchy but unable to figure it out..." % "feature")
                
            elif count_hiers:
                r.info("%s has multiple hiers so no easy way to determine parent" % "feature")
            else:
                pass

        # check wof:name

        name = props.get("wof:name", "")
        
        if len(name) == 0:
            r.debug("%s has a zero-length name" % "feature")
            
        # check ISO country

        iso = props.get("iso:country", "")
        
        if len(iso) != 2:
            r.debug("%s has a weird ISO" % path)

        # update the record?

        if updated and self.do_export:
            r.info("%s has changes that will be written to disk" % "feature")
            feature['properties'] = props
            # exporter.export_feature(feature)
    
        return r
