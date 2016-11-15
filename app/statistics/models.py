from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from app.auth.models import token_auth, Security
from app.helper.helper import Calc
import datetime
from dateutil.relativedelta import relativedelta
from collections import OrderedDict


db = SQLAlchemy(session_options={"autoflush": False})

class Statistics(): 
    HAULER_ID = -1#
    dateFrom = ''#
    dateTo = ''#
    reused = 0,#
    recycled = 0,#
    disposed = 0,#
    timelineStats = {},#
    totalProjects = 0,#
    activeProjects = 0,#
    completedProjects = 0,#
    projectsDuration = 0,
    materialsRecycled = 0,#
    facilitiesUsed = 0,#
    totalTickets = 0,#
    avgTicketWeight = 0,
    totalSqFt = 0,#
    totalDollarVal = 0,#
    projectTypes = 0,#
    avgProjectTonnage = 0#    
    chartCategories = []#    

    #STATS
    diversionRate = 0
    nonInertRate = 0
    inertRate = 0

    #CARBON FOOTPRINT
    tonsRecycledReused = 0
    projectedTonsRecycledReused = 0
    co2 = 0
    projectedCo2 = 0
    homesPowered = 0
    projectedHomesPowered = 0
    vehiclesRemoved = 0
    projectedVehiclesRemoved = 0
    oilSaved = 0
    projectedOilSaved = 0
    gasolineSaved = 0
    projectedGasolineSaved = 0
    treeCarbon = 0   
    projectedTreeCarbon = 0

    #materialsRecycled
    materialsRecycledList = {}
    totalTons = 0
    reusedPercent = 0
    recycledPercent = 0
    disposedPercent = 0

    #Facilities
    facilitiesUsedList = {}

    #Project Types
    projectTypesList = {}

    #Hauling
    debris = 0
    hauling = 0
    haulingSelf = 0



    def __init__(self, **kwargs):                
        self.HAULER_ID = Security.getHaulerId()
        try:            
            self.dateTo = datetime.datetime.strptime(kwargs.get('dateTo'), "%Y-%m-%d").date().strftime('%Y-%m-%d')
            self.dateFrom = datetime.datetime.strptime(kwargs.get('dateFrom'), "%Y-%m-%d").date().strftime('%Y-%m-%d')            
            self.activeProjects = 0
            self.completedProjects = 0
            self.totalSqFt = 0
            self.totalDollarVal = 0
            self.timelineStats = {}
            self.recycled = 0
            self.disposed = 0
            self.reused = 0
            self.totalTickets = 0            
            self.diversionRate = 0            
            self.nonInertRate = 0            
            self.inertRate = 0
            self.tonsRecycledReused = 0
            self.projectedTonsRecycledReused = 0
            self.totalProjects = 0

            self.co2 = 0
            self.projectedCo2 = 0
            self.homesPowered = 0
            self.projectedHomesPowered = 0
            self.vehiclesRemoved = 0
            self.projectedVehiclesRemoved = 0
            self.oilSaved = 0
            self.projectedOilSaved = 0
            self.gasolineSaved = 0
            self.projectedGasolineSaved = 0
            self.treeCarbon = 0   
            self.projectedTreeCarbon = 0

            self.materialsRecycledList = {}
            self.totalTons = 0
            self.reusedPercent = 0
            self.recycledPercent = 0
            self.disposedPercent = 0

            self.facilitiesUsedList = {}
            self.projectTypesList = {}

            self.debris = 0
            self.hauling = 0
            self.haulingSelf = 0

        except ValueError:
            self.dateTo = datetime.datetime.today().strftime('%Y-%m-%d')
            self.dateFrom = datetime.datetime.today().strftime('%Y-%m-%d')
    
    def dateFilter(self, filterType='rd'):
        clause = ''
        if filterType == 'rd':            
            clause += " AND DATE(tickets_rd.thedate) >= DATE('"+str(self.dateFrom)+"') "            
            clause += " AND DATE(tickets_rd.thedate) <= DATE('"+str(self.dateTo)+"') "   
        if filterType == 'sr':                        
            clause += " AND DATE(tickets_sr.thedate_ticket) >= DATE('"+str(self.dateFrom)+"') "            
            clause += " AND DATE(tickets_sr.thedate_ticket) <= DATE('"+str(self.dateTo)+"') "   
        if filterType == 'project':                        
            clause += " AND DATE(projects.thedate_start) >= DATE('"+str(self.dateFrom)+"') "            
            clause += " AND DATE(projects.thedate_start) <= DATE('"+str(self.dateTo)+"') "       
        
        return clause            

    def fulfillMonthstats(self):                
        dateRange = self.makeDateRange();
        
        for key in self.timelineStats:
            for dt in dateRange:                                
                if dt not in self.timelineStats[key]:
                    self.timelineStats[key][dt] = 0
                else:
                    self.timelineStats[key][dt] = str(self.timelineStats[key][dt])

            self.timelineStats[key] = OrderedDict(sorted(self.timelineStats[key].items()))
                

    def makeDateRange(self):
        startYM = self.dateFrom[0:7]
        endYM = self.dateTo[0:7]
        data = []
        format = '%Y-%m'
        while datetime.datetime.strptime(startYM, format).timestamp() <= datetime.datetime.strptime(endYM, format).timestamp():
            data.append(startYM)
            startYM = (datetime.datetime.strptime(startYM, format) + relativedelta(months=1)).strftime(format)            
        return(data)    

    def createChartCategories(self):
        dateRange = self.makeDateRange()

        monthsNames = {
            '01':'Jan',
            '02':'Feb',
            '03':'Mar',
            '04':'Apr',
            '05':'May',
            '06':'Jun',
            '07':'Jul',
            '08':'Aug',
            '09':'Sep',
            '10':'Oct',
            '11':'Nov',
            '12':'Dec'
        }
        chartCategories = []
        isFirst = True
        for dt in dateRange:
            parts = dt.split('-')
            if isFirst:
                chartCategories.append(monthsNames[parts[1]] + '<br/>' + parts[0])
                isFirst = False
            else:
                if parts[1] == '01':
                    chartCategories.append(monthsNames[parts[1]] + '<br>' + parts[0]) 
                else:
                    chartCategories.append(monthsNames[parts[1]])    

        return chartCategories
        

    def getProjectsIdsHavingTickets(self):    
        query = db.engine.execute("SELECT projects.PROJECT_ID \
            FROM projects \
            INNER JOIN tickets_rd ON tickets_rd.PROJECT_ID = projects.PROJECT_ID \
            WHERE tickets_rd.HAULER_ID="+ str(self.HAULER_ID) + str(self.dateFilter()) +" GROUP BY projects.PROJECT_ID")
        ids = ['0']
        projects = query.fetchall()
        if projects:
            for row in projects:
                ids.append(str(row.PROJECT_ID))

        return (','.join(ids))

    def getProjectsIds(self):    
        query = db.engine.execute("SELECT projects.PROJECT_ID FROM projects \
            LEFT JOIN projects_haulers ON projects_haulers.PROJECT_ID=projects.PROJECT_ID \
            LEFT JOIN projects_debrisbox ON projects_debrisbox.PROJECT_ID=projects.PROJECT_ID \
            LEFT JOIN projects_self_haulers ON projects_self_haulers.PROJECT_ID=projects.PROJECT_ID \
            WHERE projects.status!='not_submitted' AND projects.status!='submitted_to_city' \
            AND (projects_haulers.HAULER_ID=" + str(self.HAULER_ID) + " OR projects_self_haulers.HAULER_ID="+str(self.HAULER_ID) + " OR projects_debrisbox.HAULER_ID="+str(self.HAULER_ID) + ") GROUP BY projects.PROJECT_ID")
        
        ids = ['0']
        projects = query.fetchall()
        if projects:
            for row in projects:
                ids.append(str(row.PROJECT_ID))

        return (','.join(ids))    

    def setOverallStats(self):  
        clause_rd = self.dateFilter()
        clause_sr = self.dateFilter('sr')  
        query = db.engine.execute("SELECT tickets_rd.TICKET_RD_ID, tickets_rd.weight, tickets_rd.recycled, m.inerts  FROM tickets_rd  \
            INNER JOIN materials m ON m.MATERIAL_ID = tickets_rd.MATERIAL_ID \
            WHERE tickets_rd.HAULER_ID="+str(self.HAULER_ID)+ " " + clause_rd)

        allTicketsRd = query.fetchall()           

        inerts_mats_recycled = 0
        inerts_weight = 0
        noinerts_weight = 0
        noinerts_mats_recycled = 0
        for trd in allTicketsRd:
            self.recycled += trd.recycled                                                
            self.disposed += trd.weight - trd.recycled                                                
            if trd.inerts == 'true':
                inerts_mats_recycled +=  trd.recycled
                inerts_weight += trd.weight
            else:
                noinerts_mats_recycled +=  trd.recycled
                noinerts_weight += trd.weight               

        query = db.engine.execute("SELECT tickets_sr.TICKET_SR_ID, tickets_sr.weight, m.inerts FROM tickets_sr  \
            INNER JOIN materials m ON m.MATERIAL_ID = tickets_sr.MATERIAL_ID \
            WHERE tickets_sr.HAULER_ID="+str(self.HAULER_ID)+ " " + clause_sr)

        allTicketsSr = query.fetchall()            

        for tsr in allTicketsSr:   
            self.reused += tsr.weight           
            if tsr.inerts == 'true':
                inerts_mats_recycled +=  tsr.weight
                inerts_weight += tsr.weight
            else:
                noinerts_mats_recycled +=  tsr.weight
                noinerts_weight += tsr.weight                   
        
        self.diversionRate = Calc.rate(float(self.reused) + float(self.recycled) + float(self.disposed), float(self.reused) + float(self.recycled))                        

        if noinerts_weight > 0:
            self.nonInertRate = Calc.myRound(noinerts_mats_recycled / noinerts_weight * 100) 
        if inerts_weight > 0:
            self.inertRate = Calc.myRound(inerts_mats_recycled / inerts_weight * 100)         

        self.totalTons = Calc.myRound(self.recycled + self.disposed + self.reused)
        
        if self.recycled > 0:
            self.recycledPercent = Calc.myRound(float(self.recycled) / float(self.totalTons) * 100)        

        if self.reused > 0:
            self.reusedPercent = Calc.myRound(float(self.reused) / float(self.totalTons) * 100)        

        if self.disposed > 0:
            self.disposedPercent = Calc.myRound(float(self.disposed) / float(self.totalTons) * 100)        
                

    def recyclingTotals(self):
        clause_rd = self.dateFilter()
        clause_sr = self.dateFilter('sr')
        #projectsIdsHavingTickets = self.getProjectsIdsHavingTickets()
        projectIds = self.getProjectsIds()

        self.setOverallStats()

        #ALL PROJECTS
        query = db.engine.execute("SELECT projects.PROJECT_ID, projects.status, projects.square_footage, projects.project_value, projects.CONSTRUCTION_TYPE_ID_PROJECT FROM projects \
           WHERE projects.PROJECT_ID IN (" + projectIds + ") ")
        
        projects = query.fetchall()    
        
        #TOTAL PROJECTS
        self.totalProjects = len(projects)
        
        project_types = []
        for project in projects:            
            self.totalSqFt += project.square_footage
            self.totalDollarVal += project.project_value                                    
            
            if not project.CONSTRUCTION_TYPE_ID_PROJECT in project_types:
                project_types.append(project.CONSTRUCTION_TYPE_ID_PROJECT)

            if 'approved' == project.status:                
                self.activeProjects = self.activeProjects + 1
                
            if 'completed' == project.status:                
                self.completedProjects = self.completedProjects + 1                                            
        
        query = db.engine.execute("SELECT DATE_FORMAT(tickets_rd.thedate, '%%Y-%%m') AS month, SUM(recycled) AS R, \
            SUM(weight * (tickets_rd.percentage / 100)) - SUM(recycled) AS D FROM tickets_rd \
            WHERE tickets_rd.HAULER_ID=" + str(self.HAULER_ID) + " " + clause_rd + " GROUP BY month")                        

        monthstats = query.fetchall()    
        for item in monthstats:                        
            if 'Recycled' in self.timelineStats:
                self.timelineStats['Recycled'][item.month] = item.R
            else:
                self.timelineStats['Recycled'] = {item.month: item.R}
                
            if 'Disposed' in self.timelineStats:
                self.timelineStats['Disposed'][item.month] = item.D
            else:
                 self.timelineStats['Disposed'] = {item.month: item.D}            

        query = db.engine.execute("SELECT DATE_FORMAT(tickets_sr.thedate_ticket, '%%Y-%%m') AS month, \
            SUM(weight) AS SR FROM tickets_sr WHERE tickets_sr.HAULER_ID=" + str(self.HAULER_ID) + " " + clause_sr + " GROUP BY month")                        

        monthstats = query.fetchall()    

        for item in monthstats:                        
            if 'Reused' in self.timelineStats:
                self.timelineStats['Reused'][item.month] = item.SR
            else:
                self.timelineStats['Reused'] = {item.month: item.SR}                                                    
        
        if self.totalTons:
            self.avgProjectTonnage = Calc.myRound((float(self.totalTons)) / float(self.totalProjects))        

        self.projectTypes = len(project_types)        
        self.fulfillMonthstats()
        
        query = db.engine.execute("SELECT tickets_rd.TICKET_RD_ID, tickets_rd.FACILITY_ID, tickets_rd.MATERIAL_ID, tickets_rd.weight, tickets_rd.recycled, tickets_rd.percentage  FROM tickets_rd  \
            WHERE tickets_rd.HAULER_ID="+str(self.HAULER_ID)+ " " + clause_rd)

        allTicketsRd = query.fetchall()            

        fac_used = []
        mat_used = []        
        for trd in allTicketsRd:            
            if trd.FACILITY_ID not in fac_used:
                fac_used.append(trd.FACILITY_ID)

            if trd.MATERIAL_ID not in mat_used:
                mat_used.append(trd.MATERIAL_ID)

            self.totalTickets += 1                    

        query = db.engine.execute("SELECT tickets_sr.TICKET_SR_ID, tickets_sr.FACILITY_ID, tickets_sr.MATERIAL_ID FROM tickets_sr  \
            WHERE tickets_sr.HAULER_ID="+str(self.HAULER_ID)+ " " + clause_sr)

        allTicketsSr = query.fetchall()            

        for tsr in allTicketsSr:  
            if tsr.FACILITY_ID not in fac_used:
                fac_used.append(tsr.FACILITY_ID)          

            if tsr.MATERIAL_ID not in mat_used:
                mat_used.append(tsr.MATERIAL_ID)

            self.totalTickets += 1        
        
        self.facilitiesUsed = len(fac_used)
        self.materialsRecycled = len(mat_used)                
        if self.totalTons:
            self.avgTicketWeight = Calc.myRound((float(self.totalTons)) / float(self.totalTickets))

        query = db.engine.execute("SELECT  SUM(TO_DAYS(projects.thedate_end) - TO_DAYS(projects.thedate_start)) as project_duration FROM projects \
              WHERE projects.PROJECT_ID IN (" + projectIds + ") ")

        pd = query.fetchone()                    

        if pd[0]:
            self.projectsDuration = int(pd[0])
                        
        self.recycled = Calc.myRound(self.recycled)
        self.reused = Calc.myRound(self.reused)
        self.disposed = Calc.myRound(self.disposed)
        self.totalSqFt = Calc.myRound(self.totalSqFt)
        self.totalDollarVal = Calc.myRound(self.totalDollarVal)
        self.chartCategories = self.createChartCategories()        

        return (self)

    def carbonFootprint(self):
        clause_rd = self.dateFilter()
        clause_sr = self.dateFilter('sr')
        projectIds = self.getProjectsIds()        

        self.setOverallStats()

        query = db.engine.execute("SELECT projects_materials.*, materials.*, materials.MATERIAL_ID AS CONTEXT_ID \
          FROM materials LEFT JOIN projects_materials ON projects_materials.MATERIAL_ID=materials.MATERIAL_ID \
          AND projects_materials.PROJECT_ID in (" + projectIds + ") ORDER BY name ASC;")

        projectMats = query.fetchall()            

        for prMat in projectMats:
            if prMat.amt_recycle and float(prMat.amt_recycle) > 0:
                self.projectedTonsRecycledReused += prMat.amt_recycle
            if prMat.amt_salvage and float(prMat.amt_salvage) > 0:
                self.projectedTonsRecycledReused += prMat.amt_salvage                        

        #CARBON FOOTPRINT
        self.projectedTonsRecycledReused = Calc.myRound(self.projectedTonsRecycledReused)
        self.tonsRecycledReused = Calc.myRound(self.recycled + self.reused)        
        emission_saving_est = float(self.projectedTonsRecycledReused) * 0.907
        emission_saving = float(self.tonsRecycledReused) * 0.907

        if emission_saving > 0:
            self.co2 = Calc.myRound(emission_saving)
            self.homesPowered = Calc.myRound(emission_saving / 8.02)
            self.vehiclesRemoved = Calc.myRound(emission_saving / 5.1)
            self.oilSaved = Calc.myRound(emission_saving / 0.43)
            self.gasolineSaved = Calc.myRound(emission_saving / 0.00892)
            self.treeCarbon = Calc.myRound(emission_saving / 0.039)

        if emission_saving_est > 0:
            self.projectedCo2 = Calc.myRound(emission_saving_est)
            self.projectedHomesPowered = Calc.myRound(emission_saving_est / 8.02)
            self.projectedVehiclesRemoved = Calc.myRound(emission_saving_est / 5.1)
            self.projectedOilSaved = Calc.myRound(emission_saving_est / 0.43)
            self.projectedGasolineSaved = Calc.myRound(emission_saving_est / 0.00892)
            self.projectedTreeCarbon = Calc.myRound(emission_saving_est / 0.039)
        
        self.recycled = Calc.myRound(self.recycled)
        self.reused = Calc.myRound(self.reused)
        self.disposed = Calc.myRound(self.disposed)

        return (self)     

    def materialsRecycled(self):
        clause_rd = self.dateFilter()
        clause_sr = self.dateFilter('sr')        

        self.setOverallStats()    

        query = db.engine.execute("SELECT * FROM materials WHERE (materials.cn_id < 1) ORDER BY name ASC")        
        materials = query.fetchall()            

        for material in materials:             
            query = db.engine.execute("SELECT DATE_FORMAT(tickets_rd.thedate, '%%Y-%%m') AS month, \
                SUM(recycled) AS R, SUM(weight * (tickets_rd.percentage / 100)) - SUM(recycled) AS D \
                FROM tickets_rd \
                WHERE tickets_rd.HAULER_ID="+ str(self.HAULER_ID) +"  AND MATERIAL_ID=" + str(material.MATERIAL_ID) + " " + clause_rd + " GROUP BY month")        
            matStats = query.fetchall()                        
            mp = {}
            if matStats:                
                query = db.engine.execute("SELECT DISTINCT(tickets_rd.PROJECT_ID) FROM tickets_rd \
                    WHERE tickets_rd.HAULER_ID="+ str(self.HAULER_ID) +"  AND MATERIAL_ID=" + str(material.MATERIAL_ID) + " " + clause_rd + " ")        
                materialProjects = query.fetchall()                
                for item in materialProjects:
                    mp[item.PROJECT_ID] = True

                
                for item in matStats:
                    if material.name in self.timelineStats:
                        self.timelineStats[material.name][item.month] = item.R + item.D
                    else:
                        self.timelineStats[material.name] = {item.month: item.R + item.D}

                    if material.name in self.materialsRecycledList:
                        self.materialsRecycledList[material.name]['recycled'] += float(item.R)
                        self.materialsRecycledList[material.name]['disposed'] += float(item.D)                        
                        self.materialsRecycledList[material.name]['projects'] = len(mp)
                    else:
                       self.materialsRecycledList[material.name] = {'recycled': float(item.R), 'disposed': float(item.D), 'reused': 0, 'projects': len(mp)}


            if material.MATERIAL_ID == 7:
                query = db.engine.execute("SELECT DATE_FORMAT(tickets_sr.thedate_ticket, '%%Y-%%m') AS month, SUM(weight) AS SR, COUNT(DISTINCT(PROJECT_ID)) as projects \
                    FROM tickets_sr \
                    WHERE tickets_sr.HAULER_ID="+ str(self.HAULER_ID) +"  AND MATERIAL_ID=" + str(material.MATERIAL_ID) + " " + clause_sr + " GROUP BY month")        
                matStats = query.fetchall()
                if matStats:                
                    query = db.engine.execute("SELECT DISTINCT(tickets_sr.PROJECT_ID) FROM tickets_sr \
                        WHERE tickets_sr.HAULER_ID="+ str(self.HAULER_ID) +"  AND MATERIAL_ID=" + str(material.MATERIAL_ID) + " " + clause_sr + " ")        
                    materialProjects = query.fetchall()                
                    for item in materialProjects:
                        mp[item.PROJECT_ID] = True

                    for item in matStats:
                        if material.name in self.timelineStats:
                            if item.month in self.timelineStats[material.name]:
                                self.timelineStats[material.name][item.month] += item.SR
                            else:    
                                self.timelineStats[material.name][item.month] = item.SR
                        else:
                            self.timelineStats[material.name] = {item.month: item.SR}

                        if material.name in self.materialsRecycledList:
                            self.materialsRecycledList[material.name]['reused'] += float(item.SR)                            
                            self.materialsRecycledList[material.name]['projects'] = len(mp)
                        else:
                           self.materialsRecycledList[material.name] = {'recycled': 0, 'disposed': 0, 'reused': float(item.SR), 'projects': len(mp)}

            self.totalProjects += len(mp)

        materialsList = []
        grandTotal = float(self.totalTons)
        for mat in self.materialsRecycledList:
            self.materialsRecycledList[mat]['totalTons'] = self.materialsRecycledList[mat]['reused'] + self.materialsRecycledList[mat]['recycled'] + self.materialsRecycledList[mat]['disposed']
            self.materialsRecycledList[mat]['totalPercent'] = self.materialsRecycledList[mat]['totalTons'] / grandTotal * 100
            if self.materialsRecycledList[mat]['recycled'] > 0:
                self.materialsRecycledList[mat]['recycledPercent'] = self.materialsRecycledList[mat]['recycled'] / float(self.recycled) * 100
            else:
                self.materialsRecycledList[mat]['recycledPercent'] = 0     
            if self.materialsRecycledList[mat]['reused'] > 0:    
                self.materialsRecycledList[mat]['reusedPercent'] = self.materialsRecycledList[mat]['reused'] / float(self.reused) * 100
            else:
                self.materialsRecycledList[mat]['reusedPercent'] = 0    
            if self.materialsRecycledList[mat]['disposed'] > 0:    
                self.materialsRecycledList[mat]['disposedPercent'] = self.materialsRecycledList[mat]['disposed'] / float(self.disposed) * 100
            else:
                self.materialsRecycledList[mat]['disposedPercent'] = 0                            
            self.materialsRecycledList[mat]['name'] = mat

            materialsList.append(self.materialsRecycledList[mat])

        self.materialsRecycledList = materialsList        

        self.fulfillMonthstats()                                            
        self.chartCategories = self.createChartCategories()

        self.recycled = Calc.myRound(self.recycled)
        self.reused = Calc.myRound(self.reused)
        self.disposed = Calc.myRound(self.disposed)

        return (self)

    def facilitiesUsed(self):
        clause_rd = self.dateFilter()
        clause_sr = self.dateFilter('sr')        

        self.setOverallStats()    

        query = db.engine.execute("SELECT DISTINCT(facilities.FACILITY_ID), facilities.name FROM facilities \
            INNER JOIN tickets_rd ON tickets_rd.FACILITY_ID=facilities.FACILITY_ID \
            WHERE tickets_rd.HAULER_ID=" + str(self.HAULER_ID) + clause_rd + " AND facilities.FACILITY_ID=tickets_rd.FACILITY_ID \
            ORDER BY name ASC")        
        facs = query.fetchall()

        for fac in facs:
            fp ={}
            query = db.engine.execute("SELECT DATE_FORMAT(tickets_rd.thedate, '%%Y-%%m') AS month, SUM(recycled) AS R, \
                SUM(weight * (tickets_rd.percentage / 100)) - SUM(recycled) AS D FROM tickets_rd \
                WHERE tickets_rd.HAULER_ID="+ str(self.HAULER_ID) +" AND FACILITY_ID="+ str(fac.FACILITY_ID) + clause_rd + " GROUP BY month")        
            facStats = query.fetchall()
            if facStats:
                
                query = db.engine.execute("SELECT DISTINCT(tickets_rd.PROJECT_ID) FROM tickets_rd \
                    WHERE tickets_rd.HAULER_ID="+ str(self.HAULER_ID) +"  AND FACILITY_ID=" + str(fac.FACILITY_ID) + " " + clause_rd + " ")        
                facilityProjects = query.fetchall()                
                for item in facilityProjects:
                    fp[item.PROJECT_ID] = True                

                for item in facStats:
                    if fac.name in self.timelineStats:
                        self.timelineStats[fac.name][item.month] = item.R + item.D
                    else:
                        self.timelineStats[fac.name] = {item.month: item.R + item.D}

                    if fac.name in self.facilitiesUsedList:
                        self.facilitiesUsedList[fac.name]['recycled'] += float(item.R)
                        self.facilitiesUsedList[fac.name]['disposed'] += float(item.D)                        
                        self.facilitiesUsedList[fac.name]['projects'] = len(fp)
                    else:
                       self.facilitiesUsedList[fac.name] = {'recycled': float(item.R), 'disposed': float(item.D), 'reused': 0, 'projects': len(fp)}

            query = db.engine.execute("SELECT DATE_FORMAT(tickets_sr.thedate_ticket, '%%Y-%%m') AS month, SUM(weight) AS SR FROM tickets_sr \
                WHERE tickets_sr.HAULER_ID="+ str(self.HAULER_ID) +" AND FACILITY_ID="+ str(fac.FACILITY_ID) + clause_sr + " GROUP BY month")        
            facStats = query.fetchall()
            if facStats:

                query = db.engine.execute("SELECT DISTINCT(tickets_sr.PROJECT_ID) FROM tickets_sr \
                    WHERE tickets_sr.HAULER_ID="+ str(self.HAULER_ID) +"  AND FACILITY_ID=" + str(fac.FACILITY_ID) + " " + clause_sr + " ")        
                facilityProjects = query.fetchall()                
                for item in facilityProjects:
                    fp[item.PROJECT_ID] = True    

                for item in facStats:                    
                    if fac.name in self.timelineStats:
                        if item.month in self.timelineStats[fac.name]:
                            self.timelineStats[fac.name][item.month] += item.SR
                        else:    
                            self.timelineStats[fac.name][item.month] = item.SR
                    else:
                        self.timelineStats[fac.name] = {item.month: item.SR}

                    if fac.name in self.facilitiesUsedList:
                        self.facilitiesUsedList[fac.name]['reused'] += float(item.SR)                            
                        self.facilitiesUsedList[fac.name]['projects'] = len(fp)
                    else:
                       self.facilitiesUsedList[fac.name] = {'recycled': 0, 'disposed': 0, 'reused': float(item.SR), 'projects': len(fp)}

            self.totalProjects += len(fp)               

        facilitiesList = []
        grandTotal = float(self.totalTons)
        for fac in self.facilitiesUsedList:
            self.facilitiesUsedList[fac]['totalTons'] = self.facilitiesUsedList[fac]['reused'] + self.facilitiesUsedList[fac]['recycled'] + self.facilitiesUsedList[fac]['disposed']
            self.facilitiesUsedList[fac]['totalPercent'] = self.facilitiesUsedList[fac]['totalTons'] / grandTotal * 100
            if self.facilitiesUsedList[fac]['recycled'] > 0:
                self.facilitiesUsedList[fac]['recycledPercent'] = self.facilitiesUsedList[fac]['recycled'] / float(self.recycled) * 100
            else:
                self.facilitiesUsedList[fac]['recycledPercent'] = 0     
            if self.facilitiesUsedList[fac]['reused'] > 0:    
                self.facilitiesUsedList[fac]['reusedPercent'] = self.facilitiesUsedList[fac]['reused'] / float(self.reused) * 100
            else:
                self.facilitiesUsedList[fac]['reusedPercent'] = 0    
            if self.facilitiesUsedList[fac]['disposed'] > 0:    
                self.facilitiesUsedList[fac]['disposedPercent'] = self.facilitiesUsedList[fac]['disposed'] / float(self.disposed) * 100
            else:
                self.facilitiesUsedList[fac]['disposedPercent'] = 0                            
            self.facilitiesUsedList[fac]['name'] = fac

            facilitiesList.append(self.facilitiesUsedList[fac])

        self.facilitiesUsedList = facilitiesList

        self.fulfillMonthstats()                                            
        self.chartCategories = self.createChartCategories()
        
        self.recycled = Calc.myRound(self.recycled)
        self.reused = Calc.myRound(self.reused)
        self.disposed = Calc.myRound(self.disposed)

        return (self)        

    def projectTypes(self):
        clause_rd = self.dateFilter()
        clause_sr = self.dateFilter('sr')        

        self.setOverallStats()    

        query = db.engine.execute("SELECT construction_types.* FROM construction_types WHERE construction_types.ctype='project'")        
        ptypes = query.fetchall()

        for pt in ptypes:
            fp = {}
            query = db.engine.execute("SELECT DATE_FORMAT(tickets_rd.thedate, '%%Y-%%m') AS month, SUM(recycled) AS R, SUM(weight * (tickets_rd.percentage / 100)) - SUM(recycled) AS D FROM tickets_rd \
                INNER JOIN projects ON projects.PROJECT_ID=tickets_rd.PROJECT_ID \
                WHERE tickets_rd.HAULER_ID="+ str(self.HAULER_ID) +" AND projects.PROJECT_ID=tickets_rd.PROJECT_ID AND projects.CONSTRUCTION_TYPE_ID_PROJECT=" + str(pt.CONSTRUCTION_TYPE_ID) + clause_rd + " GROUP BY month")
            typeStats = query.fetchall()
            if typeStats:                

                query = db.engine.execute("SELECT DISTINCT(tickets_rd.PROJECT_ID) FROM tickets_rd \
                    INNER JOIN projects ON projects.PROJECT_ID=tickets_rd.PROJECT_ID \
                    WHERE tickets_rd.HAULER_ID="+ str(self.HAULER_ID) +"  AND projects.CONSTRUCTION_TYPE_ID_PROJECT=" + str(pt.CONSTRUCTION_TYPE_ID) + " " + clause_rd + " ")        
                facilityProjects = query.fetchall()                
                for item in facilityProjects:
                    fp[item.PROJECT_ID] = True                

                for item in typeStats:
                    if pt.name in self.timelineStats:
                        self.timelineStats[pt.name][item.month] = item.R + item.D
                    else:
                        self.timelineStats[pt.name] = {item.month: item.R + item.D}

                    if pt.name in self.projectTypesList:
                        self.projectTypesList[pt.name]['recycled'] += float(item.R)
                        self.projectTypesList[pt.name]['disposed'] += float(item.D)                        
                        self.projectTypesList[pt.name]['projects'] = len(fp)
                    else:
                       self.projectTypesList[pt.name] = {'recycled': float(item.R), 'disposed': float(item.D), 'reused': 0, 'projects': len(fp)}

            query = db.engine.execute("SELECT DATE_FORMAT(tickets_sr.thedate_ticket, '%%Y-%%m') AS month, SUM(weight) AS SR FROM tickets_sr  \
                INNER JOIN projects ON projects.PROJECT_ID=tickets_sr.PROJECT_ID \
                WHERE tickets_sr.HAULER_ID="+ str(self.HAULER_ID) +" AND tickets_sr.PROJECT_ID=projects.PROJECT_ID AND projects.CONSTRUCTION_TYPE_ID_PROJECT=" + str(pt.CONSTRUCTION_TYPE_ID) + clause_sr + "  GROUP BY month")
            typeStats = query.fetchall()
            if typeStats:

                query = db.engine.execute("SELECT DISTINCT(tickets_sr.PROJECT_ID) FROM tickets_sr \
                    INNER JOIN projects ON projects.PROJECT_ID=tickets_sr.PROJECT_ID \
                    WHERE tickets_sr.HAULER_ID="+ str(self.HAULER_ID) +"  AND projects.CONSTRUCTION_TYPE_ID_PROJECT=" + str(pt.CONSTRUCTION_TYPE_ID) + " " + clause_sr + " ")        
                facilityProjects = query.fetchall()                
                for item in facilityProjects:
                    fp[item.PROJECT_ID] = True                

                for item in typeStats:                    
                    if pt.name in self.timelineStats:
                        if item.month in self.timelineStats[pt.name]:
                            self.timelineStats[pt.name][item.month] += item.SR
                        else:    
                            self.timelineStats[pt.name][item.month] = item.SR
                    else:
                        self.timelineStats[pt.name] = {item.month: item.SR}

                    if pt.name in self.projectTypesList:
                        self.projectTypesList[pt.name]['reused'] += float(item.SR)                            
                        self.projectTypesList[pt.name]['projects'] = len(fp)
                    else:
                       self.projectTypesList[pt.name] = {'recycled': 0, 'disposed': 0, 'reused': float(item.SR), 'projects': len(fp)}

            self.totalProjects += len(fp)                                  

        ptList = []
        grandTotal = float(self.totalTons)
        for item in self.projectTypesList:
            self.projectTypesList[item]['totalTons'] = self.projectTypesList[item]['reused'] + self.projectTypesList[item]['recycled'] + self.projectTypesList[item]['disposed']
            self.projectTypesList[item]['totalPercent'] = self.projectTypesList[item]['totalTons'] / grandTotal * 100
            if self.projectTypesList[item]['recycled'] > 0:
                self.projectTypesList[item]['recycledPercent'] = self.projectTypesList[item]['recycled'] / float(self.recycled) * 100
            else:
                self.projectTypesList[item]['recycledPercent'] = 0     
            if self.projectTypesList[item]['reused'] > 0:    
                self.projectTypesList[item]['reusedPercent'] = self.projectTypesList[item]['reused'] / float(self.reused) * 100
            else:
                self.projectTypesList[item]['reusedPercent'] = 0    
            if self.projectTypesList[item]['disposed'] > 0:    
                self.projectTypesList[item]['disposedPercent'] = self.projectTypesList[item]['disposed'] / float(self.disposed) * 100
            else:
                self.projectTypesList[item]['disposedPercent'] = 0                            
            self.projectTypesList[item]['name'] = item

            ptList.append(self.projectTypesList[item])

        self.projectTypesList = ptList    
        
        self.fulfillMonthstats()                                            
        self.chartCategories = self.createChartCategories()
        
        self.recycled = Calc.myRound(self.recycled)
        self.reused = Calc.myRound(self.reused)
        self.disposed = Calc.myRound(self.disposed)

        return (self)    

    def buildingTypes(self):
        clause_rd = self.dateFilter()
        clause_sr = self.dateFilter('sr')        

        self.setOverallStats()    

        query = db.engine.execute("SELECT construction_types.* FROM construction_types WHERE construction_types.ctype='building'")        
        ptypes = query.fetchall()

        for pt in ptypes:
            fp = {}
            query = db.engine.execute("SELECT DATE_FORMAT(tickets_rd.thedate, '%%Y-%%m') AS month, SUM(recycled) AS R, SUM(weight * (tickets_rd.percentage / 100)) - SUM(recycled) AS D FROM tickets_rd \
                INNER JOIN projects ON projects.PROJECT_ID=tickets_rd.PROJECT_ID \
                WHERE tickets_rd.HAULER_ID="+ str(self.HAULER_ID) +" AND projects.PROJECT_ID=tickets_rd.PROJECT_ID AND projects.CONSTRUCTION_TYPE_ID_BUILDING=" + str(pt.CONSTRUCTION_TYPE_ID) + clause_rd + " GROUP BY month")
            typeStats = query.fetchall()
            if typeStats:                

                query = db.engine.execute("SELECT DISTINCT(tickets_rd.PROJECT_ID) FROM tickets_rd \
                    INNER JOIN projects ON projects.PROJECT_ID=tickets_rd.PROJECT_ID \
                    WHERE tickets_rd.HAULER_ID="+ str(self.HAULER_ID) +"  AND projects.CONSTRUCTION_TYPE_ID_BUILDING=" + str(pt.CONSTRUCTION_TYPE_ID) + " " + clause_rd + " ")        
                facilityProjects = query.fetchall()                
                for item in facilityProjects:
                    fp[item.PROJECT_ID] = True                

                for item in typeStats:
                    if pt.name in self.timelineStats:
                        self.timelineStats[pt.name][item.month] = item.R + item.D
                    else:
                        self.timelineStats[pt.name] = {item.month: item.R + item.D}

                    if pt.name in self.projectTypesList:
                        self.projectTypesList[pt.name]['recycled'] += float(item.R)
                        self.projectTypesList[pt.name]['disposed'] += float(item.D)                        
                        self.projectTypesList[pt.name]['projects'] = len(fp)
                    else:
                       self.projectTypesList[pt.name] = {'recycled': float(item.R), 'disposed': float(item.D), 'reused': 0, 'projects': len(fp)}

            query = db.engine.execute("SELECT DATE_FORMAT(tickets_sr.thedate_ticket, '%%Y-%%m') AS month, SUM(weight) AS SR FROM tickets_sr  \
                INNER JOIN projects ON projects.PROJECT_ID=tickets_sr.PROJECT_ID \
                WHERE tickets_sr.HAULER_ID="+ str(self.HAULER_ID) +" AND tickets_sr.PROJECT_ID=projects.PROJECT_ID AND projects.CONSTRUCTION_TYPE_ID_BUILDING=" + str(pt.CONSTRUCTION_TYPE_ID) + clause_sr + "  GROUP BY month")
            typeStats = query.fetchall()
            if typeStats:

                query = db.engine.execute("SELECT DISTINCT(tickets_sr.PROJECT_ID) FROM tickets_sr \
                    INNER JOIN projects ON projects.PROJECT_ID=tickets_sr.PROJECT_ID \
                    WHERE tickets_sr.HAULER_ID="+ str(self.HAULER_ID) +"  AND projects.CONSTRUCTION_TYPE_ID_BUILDING=" + str(pt.CONSTRUCTION_TYPE_ID) + " " + clause_sr + " ")        
                facilityProjects = query.fetchall()                
                for item in facilityProjects:
                    fp[item.PROJECT_ID] = True                

                for item in typeStats:                    
                    if pt.name in self.timelineStats:
                        if item.month in self.timelineStats[pt.name]:
                            self.timelineStats[pt.name][item.month] += item.SR
                        else:    
                            self.timelineStats[pt.name][item.month] = item.SR
                    else:
                        self.timelineStats[pt.name] = {item.month: item.SR}

                    if pt.name in self.projectTypesList:
                        self.projectTypesList[pt.name]['reused'] += float(item.SR)                            
                        self.projectTypesList[pt.name]['projects'] = len(fp)
                    else:
                       self.projectTypesList[pt.name] = {'recycled': 0, 'disposed': 0, 'reused': float(item.SR), 'projects': len(fp)}

            self.totalProjects += len(fp)                                  

        ptList = []
        grandTotal = float(self.totalTons)
        for item in self.projectTypesList:
            self.projectTypesList[item]['totalTons'] = self.projectTypesList[item]['reused'] + self.projectTypesList[item]['recycled'] + self.projectTypesList[item]['disposed']
            self.projectTypesList[item]['totalPercent'] = self.projectTypesList[item]['totalTons'] / grandTotal * 100
            if self.projectTypesList[item]['recycled'] > 0:
                self.projectTypesList[item]['recycledPercent'] = self.projectTypesList[item]['recycled'] / float(self.recycled) * 100
            else:
                self.projectTypesList[item]['recycledPercent'] = 0     
            if self.projectTypesList[item]['reused'] > 0:    
                self.projectTypesList[item]['reusedPercent'] = self.projectTypesList[item]['reused'] / float(self.reused) * 100
            else:
                self.projectTypesList[item]['reusedPercent'] = 0    
            if self.projectTypesList[item]['disposed'] > 0:    
                self.projectTypesList[item]['disposedPercent'] = self.projectTypesList[item]['disposed'] / float(self.disposed) * 100
            else:
                self.projectTypesList[item]['disposedPercent'] = 0                            
            self.projectTypesList[item]['name'] = item

            ptList.append(self.projectTypesList[item])

        self.projectTypesList = ptList    
        
        self.fulfillMonthstats()                                            
        self.chartCategories = self.createChartCategories()
        
        self.recycled = Calc.myRound(self.recycled)
        self.reused = Calc.myRound(self.reused)
        self.disposed = Calc.myRound(self.disposed)

        return (self)        

    def haulingTypes(self):
        clause_rd = self.dateFilter()
        clause_sr = self.dateFilter('sr')
        clause_project = self.dateFilter('project')
        projectIds = self.getProjectsIds()               

        self.setOverallStats()    

        query = db.engine.execute("SELECT COUNT(*) FROM projects \
            WHERE PROJECT_ID IN ("+ projectIds +") AND haul_debrisbox='true' " + clause_project)
        debris = query.fetchone()
        if debris:
            self.debris = debris[0]

        query = db.engine.execute("SELECT COUNT(*) FROM projects \
            WHERE PROJECT_ID IN ("+ projectIds +") AND haul_service='true' " + clause_project)
        haul = query.fetchone()
        if haul:
            self.hauling = haul[0]    

        query = db.engine.execute("SELECT COUNT(*) FROM projects \
            WHERE PROJECT_ID IN ("+ projectIds +") AND haul_self='true' " + clause_project)
        haul_self = query.fetchone()
        if haul_self:
            self.haulingSelf = haul_self[0]     

        query = db.engine.execute("SELECT DATE_FORMAT(projects.thedate_start, '%%Y-%%m') AS month, COUNT(*) AS debris \
            FROM projects WHERE PROJECT_ID IN ("+ projectIds +") " + clause_project +" AND projects.haul_debrisbox='true' GROUP BY month")       
        monthstats = query.fetchall()                

        for item in monthstats:
            if 'debris' in self.timelineStats:
                self.timelineStats['debris'][item.month] = item.debris
            else:
                self.timelineStats['debris'] = {item.month: item.debris}

        query = db.engine.execute("SELECT DATE_FORMAT(projects.thedate_start, '%%Y-%%m') AS month, COUNT(*) AS service \
            FROM projects WHERE PROJECT_ID IN ("+ projectIds +") " + clause_project +" AND projects.haul_service='true' GROUP BY month")       
        monthstats = query.fetchall()                

        for item in monthstats:
            if 'service' in self.timelineStats:
                self.timelineStats['service'][item.month] = item.service
            else:
                self.timelineStats['service'] = {item.month: item.service}        

        query = db.engine.execute("SELECT DATE_FORMAT(projects.thedate_start, '%%Y-%%m') AS month, COUNT(*) AS self_hauler \
            FROM projects WHERE PROJECT_ID IN ("+ projectIds +") " + clause_project +" AND projects.haul_self='true' GROUP BY month")       
        monthstats = query.fetchall()                

        for item in monthstats:
            if 'self_hauler' in self.timelineStats:
                self.timelineStats['self_hauler'][item.month] = item.self_hauler
            else:
                self.timelineStats['self_hauler'] = {item.month: item.self_hauler}                                        
        

        self.fulfillMonthstats()                                            
        self.chartCategories = self.createChartCategories()

        self.recycled = Calc.myRound(self.recycled)
        self.reused = Calc.myRound(self.reused)
        self.disposed = Calc.myRound(self.disposed)

        return (self)            
