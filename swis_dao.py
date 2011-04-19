import datetime

from sqlalchemy import create_engine, distinct, func
from sqlalchemy.orm import mapper, scoped_session, sessionmaker
from sqlalchemy.sql import and_

import wof
import sqlalch_swis_models as model

from wof.base_dao import BaseDao

class SwisDao(BaseDao):
    
    def __init__(self, db_connection_string):
        self.engine = create_engine(db_connection_string, convert_unicode=True)
        self.db_session = scoped_session(sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine))
        model.init_model(self.db_session)
    
    def get_all_sites(self):
        return model.Site.query.all()
    
    def get_site_by_code(self, site_code):
        return model.Site.query.filter(
            model.Site.SiteCode == site_code).first()
    
    def get_sites_by_codes(self, site_codes_arr):
        return model.Site.query.filter(
            model.Site.SiteCode.in_(site_codes_arr)).all()
    
    def get_all_variables(self):
        return model.Variable.query.all()
    
    def get_variable_by_code(self, var_code):
        return model.Variable.query.filter(
            model.Variable.VariableCode == var_code).first()
    
    def get_variables_by_codes(self, var_codes_arr):
        return model.Variable.query.filter(model.Variable.VariableCode.in_(
            var_codes_arr)).all()
    
    def get_series_by_sitecode(self, site_code):
        
        siteResult = model.Site.query.filter(
            model.Site.SiteCode==site_code).one()
        
        if siteResult:
            
            resultList = self.db_session.query(
                model.DataValue.VariableID.label('VariableID'),
                func.count(model.DataValue.DataValue).label('ValueCount'),
                func.min(model.DataValue.DateTimeUTC).label(
                    'BeginDateTimeUTC'),
                func.max(model.DataValue.DateTimeUTC).label('EndDateTimeUTC'),
                model.DataValue.UTCOffset.label('UTCOffset')
            ).group_by(
                model.DataValue.VariableID).filter(
                    model.DataValue.SiteID==siteResult.SiteID
                ).order_by(model.DataValue.VariableID).all()
            
            varIDArr = [r.VariableID for r in resultList]

            varResultArr = model.Variable.query.filter(
                model.Variable.VariableID.in_(varIDArr)).order_by(
                    model.Variable.VariableID).all()

            seriesCatArr = []
            for i in range(len(resultList)):

                begin_date = None
                end_date = None

                if resultList[i].UTCOffset:
                    offset_delta = datetime.timedelta(
                        hours=resultList[i].UTCOffset)
                    
                    begin_date = resultList[i].BeginDateTimeUTC + offset_delta
                    end_date = resultList[i].EndDateTimeUTC + offset_delta
                
                seriesCat = model.SeriesCatalog(
                    siteResult, varResultArr[i],
                    resultList[i].ValueCount,
                    resultList[i].BeginDateTimeUTC,
                    resultList[i].EndDateTimeUTC,
                    begin_date, end_date)
                               
                seriesCatArr.append(seriesCat)
            return seriesCatArr
            
        return None
    
    def get_series_by_sitecode_and_varcode(self, site_code, var_code):
        siteResult = model.Site.query.filter(model.Site.SiteCode==site_code).one()
        varResult = model.Variable.query.filter(
            model.Variable.VariableCode==var_code).one()
                
        res = self.db_session.query(
                func.count(model.DataValue.DataValue).label('ValueCount'),
                func.min(model.DataValue.DateTimeUTC).label('BeginDateTimeUTC'),
                func.max(model.DataValue.DateTimeUTC).label('EndDateTimeUTC'),
                model.DataValue.UTCOffset.label('UTCOffset')
            ).filter(and_(model.DataValue.SiteID==siteResult.SiteID,
                        model.DataValue.VariableID==varResult.VariableID)).one()
            
        begin_date = None
        end_date = None
                
        if res.UTCOffset:
            offset_delta = datetime.timedelta(hours=res.UTCOffset)
            
            begin_date = res.BeginDateTimeUTC + offset_delta
            end_date = res.EndDateTimeUTC + offset_delta

        seriesCat = model.SeriesCatalog(
            siteResult, varResult, res.ValueCount, res.BeginDateTimeUTC,
            res.EndDateTimeUTC, begin_date, end_date)
       
        return [seriesCat]
         
    #TODO
    def get_datavalues(self, site_code, var_code, begin_date_time=None,
                       end_date_time=None):
        
        #first find the site and variable
        siteResult = self.get_site_by_code(site_code)
        varResult = self.get_variable_by_code(var_code)
        
        valueResultArr = None
        
        #TODO: Should we be using DateTimeUTC instead of LocalDateTime?
        # All the other WOF services uses local
        
        if (not begin_date_time or not end_date_time):
            valueResultArr = model.DataValue.query.filter(
                and_(model.DataValue.SiteID == siteResult.SiteID,
                     model.DataValue.VariableID == varResult.VariableID)
                ).order_by(model.DataValue.DateTimeUTC).all()
        else:
            valueResultArr = model.DataValue.query.filter(
                and_(model.DataValue.SiteID == siteResult.SiteID,
                     model.DataValue.VariableID == varResult.VariableID,
                     model.DataValue.DateTimeUTC >= begin_date_time, #TODO: SWIS doesn't have localdatetime
                     model.DataValue.DateTimeUTC <= end_date_time) #TODO: SWIS doesn't have localdatetime
                ).order_by(model.DataValue.DateTimeUTC).all()
            
        return valueResultArr
    
    def get_method_by_id(self, methodID):
        return model.Method.query.filter(model.Method.MethodID == methodID).first()
        
    def get_methods_by_ids(self, method_id_arr):
        return model.Method.query.filter(
            model.Method.MethodID.in_(method_id_arr)).all()
        
    def get_source_by_id(self, source_id):
        source = model.Source()
        source.ContactName = wof.contact_info['name']
        source.Phone = wof.contact_info['phone']
        source.Email = wof.contact_info['email']
        source.Organization = wof.contact_info['organization']
        source.SourceLink = wof.contact_info['link']
        source.SourceDescription = wof.contact_info['description']
        source.Address = wof.contact_info['address']
        source.City = wof.contact_info['city']
        source.State = wof.contact_info['state']
        source.ZipCode = wof.contact_info['zipcode']
        
        return source
        
    def get_sources_by_ids(self, source_id_arr):
        #There is only ever one Source for SWIS: TWDB
        return [self.get_source_by_id(1)]
    
    def get_qualifier_by_id(self, qualifier_id):
        return model.Qualifier()
    
    def get_qualifiers_by_ids(self, qualifier_id_arr):
        return [model.Qualifier()]
    
    def get_qualcontrollvl_by_id(self, qual_control_lvl_id):
        return model.QualityControlLevel()
    
    def get_qualcontrollvls_by_ids(self, qual_control_lvl_id_arr):
        return [model.QualityControlLevel()]
    
    def get_offsettype_by_id(self, offset_type_id):
        #TODO
        return None
    
    def get_offsettypes_by_ids(self, offset_type_id_arr):
        #TODO
        return None
        