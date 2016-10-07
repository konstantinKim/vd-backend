from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from app.auth.models import token_auth, Security
import datetime

db = SQLAlchemy(session_options={"autoflush": False})

class Statistics(): 
    HAULER_ID = -1
    dateFrom = ''
    dateTo = ''
    reused = 0,
    recycled = 0,
    disposed = 0,
    timelineStats = [],
    totalProjects = 0,
    activeProjects = 0,
    completedProjects = 0,
    projectsDuration = 0,
    materialsRecycled = 0,
    facilitiesUsed = 0,
    totalTickets = 0,
    avgTicketWeight = 0,
    totalSqFt = 0,
    totalDollarVal = 0,
    projectTypes = 0,
    avgProjectTonnage = 0    

    def __init__(self, **kwargs):                
        self.HAULER_ID = Security.getHaulerId()
        try:            
            self.dateTo = datetime.datetime.strptime(kwargs.get('dateTo'), "%Y-%m-%d").date().strftime('%Y-%m-%d')
            self.dateFrom = datetime.datetime.strptime(kwargs.get('dateFrom'), "%Y-%m-%d").date().strftime('%Y-%m-%d')            
        except ValueError:
            self.dateTo = datetime.datetime.today().strftime('%Y-%m-%d')
            self.dateFrom = datetime.datetime.today().strftime('%Y-%m-%d')
    
    def dateFilter(self, filterType='rd'):
        clause = ''
        if filterType == 'rd':            
            clause += " AND DATE(tickets_rd.thedate) >= DATE('"+str(self.dateFrom)+"') "            
            clause += " AND DATE(tickets_rd.thedate) <= DATE('"+str(self.dateTo)+"') "   
        if filterType == 'sr':                        
            pass
        
        return clause        

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

    def recyclingTotals(self):
        clause_rd = self.dateFilter();
        projectsIds = self.getProjectsIdsHavingTickets()

        #ALL PROJECTS
        query = db.engine.execute("SELECT projects.PROJECT_ID, projects.status, projects.square_footage, projects.project_value, projects.CONSTRUCTION_TYPE_ID_PROJECT FROM projects \
            LEFT JOIN projects_haulers ON projects_haulers.PROJECT_ID=projects.PROJECT_ID \
            LEFT JOIN projects_debrisbox ON projects_debrisbox.PROJECT_ID=projects.PROJECT_ID \
            WHERE projects.status!='not_submitted' AND projects.status!='submitted_to_city' \
            AND (projects_haulers.HAULER_ID=" + str(self.HAULER_ID) + " OR projects_debrisbox.HAULER_ID="+str(self.HAULER_ID) + ") GROUP BY projects.PROJECT_ID")

        active_ids = ['0']
        projects = query.fetchall()    
        self.totalProjects = len(projects)
        project_types = []
        for project in projects:
            active_ids.append(project.PROJECT_ID)
            #self.totalSqFt += project.square_footage
            #self.totalDollarVal += project.project_value            
            
            if not project.CONSTRUCTION_TYPE_ID_PROJECT in project_types:
                project_types.append(project.CONSTRUCTION_TYPE_ID_PROJECT)

            if 'approved' == project.status:
                self.activeProjects += 1
                pass
            if 'completed' == project.status:
                #self.completedProjects += 1                    
                pass

        #self.projectTypes = len(project_types)        
                
        return (self)


        