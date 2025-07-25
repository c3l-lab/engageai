import requests
import json
import pandas as pd
import pymysql
from datetime import datetime, timedelta
import logging
# from azure.identity import DefaultAzureCredential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MoodleDataService:
    """Service to interact with Moodle data via Web Services"""
    
    def __init__(self, moodle_url, token):
        self.moodle_url = moodle_url.rstrip('/')
        self.token = token
        self.rest_format = 'json'
    
    # def get_all_users(self, criteria=None):
    #     """Get all users or users matching criteria"""
        
    #     params = {}
    #     if criteria:
    #         # Example criteria: [{'key': 'email', 'value': 'user@example.com'}]
    #         for i, criterion in enumerate(criteria):
    #             params[f'criteria[{i}][key]'] = criterion['key']
    #             params[f'criteria[{i}][value]'] = criterion['value']
        
    #     return self._call_web_service('core_user_get_users', params)
    
    def get_courses(self, course_ids=None):
        """Get course information"""
        
        params = {}
        if course_ids:
            for i, course_id in enumerate(course_ids):
                params[f'options[ids][{i}]'] = course_id
        
        return self._call_web_service('core_course_get_courses', params)
    
    def get_course_contents(self, course_id):
        """Get course contents (sections, activities, resources)"""
        
        params = {'courseid': course_id}
        return self._call_web_service('core_course_get_contents', params)
    
    def get_enrolled_users(self, course_id):
        """Get users enrolled in a course"""
        
        params = {'courseid': course_id}
        return self._call_web_service('core_enrol_get_enrolled_users', params)
    
    def get_user_courses(self, user_id):
        """Get courses a user is enrolled in"""
        
        params = {'userid': user_id}
        return self._call_web_service('core_enrol_get_users_courses', params)
    
    def get_assignment_submissions(self, assignment_id):
        """Get assignment submissions"""
        
        params = {'assignmentid': assignment_id}
        return self._call_web_service('mod_assign_get_submissions', params)
    
    def get_quiz_attempts(self, quiz_id):
        """Get quiz attempts"""
        
        params = {'quizid': quiz_id}
        return self._call_web_service('mod_quiz_get_quiz_attempts', params)
    
    def get_gradebook_grades(self, course_id, user_id=None):
        """Get grades from gradebook"""
        
        params = {'courseid': course_id}
        if user_id:
            params['userid'] = user_id
            
        return self._call_web_service('core_grades_get_grades', params)
    
    def get_forum_discussions(self, forum_id):
        """Get forum discussions"""
        
        params = {'forumid': forum_id}
        return self._call_web_service('mod_forum_get_forum_discussions', params)
    
    def search_users_by_field(self, field, values):
        """Search users by specific field (email, username, etc.)"""
        
        params = {'field': field}
        for i, value in enumerate(values):
            params[f'values[{i}]'] = value
            
        return self._call_web_service('core_user_get_users_by_field', params)
    
    def get_user_profile(self, user_id):
        """Get detailed user profile"""
        
        params = {'userids[0]': user_id}
        return self._call_web_service('core_user_get_users_by_field', params)
    
    def _call_web_service(self,function_name, params=None):
        """Make API call to Moodle web service"""
        url = f"{self.moodle_url}/webservice/rest/server.php?"
        # https://moodle.c3l.ai/webservice/rest/server.php?
        
        # Prepare POST data parameters
        data = {
            'wstoken': self.token,
            'wsfunction': function_name,
            'moodlewsrestformat': self.rest_format,
            "criteria[0][key]": "email",   # or "email", "username", etc.
            "criteria[0][value]":  "%",
        }
        
        if params:
            data.update(params)

        
        try:
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if isinstance(result, dict) and 'exception' in result:
                logger.error(f"Moodle error: {result}")
                return None
                
            return result
            
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None
    
    def get_all_users(self, criteria=None):
        params = {}
        print(f"Inner class Token:{self.token}")
        if criteria:
            for i, criterion in enumerate(criteria):
                params[f'criteria[{i}][key]'] = criterion['key']
                params[f'criteria[{i}][value]'] = criterion['value']
        return self._call_web_service('core_user_get_users', params)

    
    # def _call_web_service(self, function_name, params=None):
    #     """Make API call to Moodle web service"""
        
    #     url = f"{self.moodle_url}/webservice/rest/server.php"
        
    #     data = {
    #         'wstoken': self.token,
    #         'wsfunction': function_name,
    #         'moodlewsrestformat': self.rest_format
    #     }
        
    #     if params:
    #         data.update(params)
        
    #     try:
    #         response = requests.post(url, data=data, timeout=30)
    #         response.raise_for_status()
            
    #         result = response.json()
            
    #         if isinstance(result, dict) and 'exception' in result:
    #             logger.error(f"Moodle error: {result}")
    #             return None
                
    #         return result
            
    #     except Exception as e:
    #         logger.error(f"Request failed: {e}")
    #         return None

class MoodleDirectDBService:
    """Service to interact directly with Moodle database"""
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
        
    def connect(self):
        """Connect to Moodle database"""
        try:
            self.connection = pymysql.connect(
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database'],
                port=self.db_config.get('port', 3306),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def get_users_data(self, active_only=True):
        """Get users data from database"""
        
        condition = "WHERE deleted = 0 AND suspended = 0" if active_only else ""
        
        query = f"""
        SELECT 
            id, username, email, firstname, lastname, 
            department, institution, city, country,
            timecreated, timemodified, lastlogin, lastaccess
        FROM mdl_user 
        {condition}
        ORDER BY lastname, firstname
        """
        
        return self._execute_query(query)
    
    def get_course_data(self, visible_only=True):
        """Get course data"""
        
        condition = "WHERE visible = 1" if visible_only else ""
        
        query = f"""
        SELECT 
            id, fullname, shortname, summary, 
            startdate, enddate, timecreated, timemodified,
            category, format, lang
        FROM mdl_course 
        {condition}
        ORDER BY fullname
        """
        
        return self._execute_query(query)
    
    def get_enrollment_data(self, course_id=None):
        """Get enrollment data"""
        
        course_filter = f"AND c.id = {course_id}" if course_id else ""
        
        query = f"""
        SELECT 
            u.id as user_id, u.username, u.email, u.firstname, u.lastname,
            c.id as course_id, c.fullname as course_name, c.shortname,
            ue.timecreated as enrollment_date, ue.timemodified,
            r.shortname as role
        FROM mdl_user u
        JOIN mdl_user_enrolments ue ON u.id = ue.userid
        JOIN mdl_enrol e ON ue.enrolid = e.id
        JOIN mdl_course c ON e.courseid = c.id
        JOIN mdl_role_assignments ra ON u.id = ra.userid
        JOIN mdl_role r ON ra.roleid = r.id
        WHERE u.deleted = 0 AND ue.status = 0 {course_filter}
        ORDER BY c.fullname, u.lastname, u.firstname
        """
        
        return self._execute_query(query)
    
    def get_grades_data(self, course_id=None, user_id=None):
        """Get grades data"""
        
        filters = []
        if course_id:
            filters.append(f"c.id = {course_id}")
        if user_id:
            filters.append(f"u.id = {user_id}")
            
        where_clause = "WHERE " + " AND ".join(filters) if filters else ""
        
        query = f"""
        SELECT 
            u.id as user_id, u.username, u.firstname, u.lastname,
            c.id as course_id, c.fullname as course_name,
            gi.itemname as grade_item, gi.itemtype, gi.itemmodule,
            gg.finalgrade, gg.rawgrade, gg.timemodified as grade_time,
            gi.grademax, gi.grademin
        FROM mdl_user u
        JOIN mdl_grade_grades gg ON u.id = gg.userid
        JOIN mdl_grade_items gi ON gg.itemid = gi.id
        JOIN mdl_course c ON gi.courseid = c.id
        {where_clause}
        ORDER BY c.fullname, u.lastname, gi.itemname
        """
        
        return self._execute_query(query)
    
    def get_activity_completion_data(self, course_id=None):
        """Get activity completion data"""
        
        course_filter = f"AND c.id = {course_id}" if course_id else ""
        
        query = f"""
        SELECT 
            u.id as user_id, u.username, u.firstname, u.lastname,
            c.id as course_id, c.fullname as course_name,
            cm.id as activity_id, m.name as activity_type,
            cmc.completionstate, cmc.timemodified as completion_time
        FROM mdl_user u
        JOIN mdl_course_modules_completion cmc ON u.id = cmc.userid
        JOIN mdl_course_modules cm ON cmc.coursemoduleid = cm.id
        JOIN mdl_course c ON cm.course = c.id
        JOIN mdl_modules m ON cm.module = m.id
        WHERE u.deleted = 0 {course_filter}
        ORDER BY c.fullname, u.lastname, cm.id
        """
        
        return self._execute_query(query)
    
    def get_login_history(self, days=30):
        """Get login history for recent days"""
        
        cutoff_time = int((datetime.now() - timedelta(days=days)).timestamp())
        
        query = f"""
        SELECT 
            u.id as user_id, u.username, u.firstname, u.lastname,
            u.lastlogin, u.lastaccess, u.currentlogin
        FROM mdl_user u
        WHERE u.deleted = 0 AND u.lastlogin > {cutoff_time}
        ORDER BY u.lastlogin DESC
        """
        
        return self._execute_query(query)
    
    def _execute_query(self, query):
        """Execute database query and return results"""
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return results
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []

class LocalDataProcessor:
    """Process and analyze local Moodle data"""
    
    def __init__(self, data_source):
        self.data_source = data_source
        
    def create_user_dataframe(self):
        """Create pandas DataFrame from user data"""
        
        if hasattr(self.data_source, 'get_all_users'):
            # Web service data
            users = self.data_source.get_all_users()
        else:
            # Database data
            users = self.data_source.get_users_data()
            
        if users:
            df = pd.DataFrame(users)
            # Convert timestamps if needed
            if 'timecreated' in df.columns:
                df['timecreated'] = pd.to_datetime(df['timecreated'], unit='s')
            if 'lastlogin' in df.columns:
                df['lastlogin'] = pd.to_datetime(df['lastlogin'], unit='s')
            return df
        return pd.DataFrame()
    
    def create_enrollment_dataframe(self):
        """Create pandas DataFrame from enrollment data"""
        
        if hasattr(self.data_source, 'get_enrollment_data'):
            enrollments = self.data_source.get_enrollment_data()
            if enrollments:
                df = pd.DataFrame(enrollments)
                if 'enrollment_date' in df.columns:
                    df['enrollment_date'] = pd.to_datetime(df['enrollment_date'], unit='s')
                return df
        return pd.DataFrame()
    
    def create_grades_dataframe(self):
        """Create pandas DataFrame from grades data"""
        
        if hasattr(self.data_source, 'get_grades_data'):
            grades = self.data_source.get_grades_data()
            if grades:
                df = pd.DataFrame(grades)
                if 'grade_time' in df.columns:
                    df['grade_time'] = pd.to_datetime(df['grade_time'], unit='s')
                return df
        return pd.DataFrame()
    
    def analyze_user_activity(self):
        """Analyze user activity patterns"""
        
        df = self.create_user_dataframe()
        if df.empty:
            return None
            
        analysis = {
            'total_users': len(df),
            'active_users_last_30_days': len(df[df['lastlogin'] > (datetime.now() - timedelta(days=30))]),
            'new_users_last_30_days': len(df[df['timecreated'] > (datetime.now() - timedelta(days=30))]),
            'users_by_country': df['country'].value_counts().to_dict() if 'country' in df.columns else {},
            'users_by_department': df['department'].value_counts().to_dict() if 'department' in df.columns else {}
        }
        
        return analysis
    
    def analyze_course_enrollment(self):
        """Analyze course enrollment patterns"""
        
        df = self.create_enrollment_dataframe()
        if df.empty:
            return None
            
        analysis = {
            'total_enrollments': len(df),
            'enrollments_by_course': df['course_name'].value_counts().to_dict(),
            'enrollments_by_role': df['role'].value_counts().to_dict() if 'role' in df.columns else {},
            'recent_enrollments': len(df[df['enrollment_date'] > (datetime.now() - timedelta(days=7))])
        }
        
        return analysis
    
    def identify_at_risk_students(self):
        """Identify students who might be at risk"""
        
        # Get users and their activity
        users_df = self.create_user_dataframe()
        grades_df = self.create_grades_dataframe()
        
        if users_df.empty:
            return []
            
        at_risk_students = []
        
        # Students who haven't logged in for 14+ days
        cutoff_date = datetime.now() - timedelta(days=14)
        inactive_users = users_df[users_df['lastlogin'] < cutoff_date]
        
        for _, user in inactive_users.iterrows():
            at_risk_students.append({
                'user_id': user['id'],
                'username': user['username'],
                'name': f"{user['firstname']} {user['lastname']}",
                'email': user['email'],
                'risk_factor': 'inactive_login',
                'last_login': user['lastlogin'],
                'details': f"Last login: {user['lastlogin']}"
            })
        
        # Students with low grades (if grade data available)
        if not grades_df.empty:
            low_grade_threshold = 60  # Adjust as needed
            low_grades = grades_df[grades_df['finalgrade'] < low_grade_threshold]
            
            for _, grade in low_grades.iterrows():
                at_risk_students.append({
                    'user_id': grade['user_id'],
                    'username': grade['username'],
                    'name': f"{grade['firstname']} {grade['lastname']}",
                    'risk_factor': 'low_grades',
                    'details': f"Grade: {grade['finalgrade']} in {grade['grade_item']}"
                })
        
        return at_risk_students

# Example usage combining Azure data with Moodle data
class AzureMoodleDataIntegration:
    """Integration class to combine Azure triggers with Moodle data analysis"""
    
    def __init__(self, moodle_service, azure_monitor):
        self.moodle = moodle_service
        self.azure = azure_monitor
        self.processor = LocalDataProcessor(moodle_service)
    
    def process_azure_trigger_with_moodle_data(self, azure_trigger_data):
        """Process Azure trigger and enrich with Moodle data"""
        
        # Get relevant Moodle data based on Azure trigger
        if azure_trigger_data.get('type') == 'user_performance':
            # Get user data from Moodle
            user_email = azure_trigger_data.get('user_email')
            users = self.moodle.search_users_by_field('email', [user_email])
            
            if users:
                user = users[0]
                # Get user's courses and grades
                courses = self.moodle.get_user_courses(user['id'])
                
                # Create enriched notification
                notification = {
                    'user_id': user['id'],
                    'user_email': user['email'],
                    'azure_data': azure_trigger_data,
                    'moodle_courses': courses,
                    'subject': f"Performance Alert for {user['firstname']} {user['lastname']}",
                    'message': self._create_enriched_message(azure_trigger_data, user, courses)
                }
                
                return notification
        
        return None
    
    def _create_enriched_message(self, azure_data, user, courses):
        """Create enriched notification message"""
        
        message = f"""
        Dear {user['firstname']},
        
        Based on data from Azure and your Moodle activity:
        
        Azure Alert: {azure_data.get('message', 'Performance concern detected')}
        
        Your current courses: {', '.join([c['fullname'] for c in courses])}
        
        Please review your progress and contact support if needed.
        """
        
        return message.strip()

# Main execution example
if __name__ == "__main__":
    # Configuration
    MOODLE_URL = "https://moodle.c3l.ai/"
    WEB_SERVICE_TOKEN = "4ba3fd94d4276b536e2958c7a575e00b"
    token= "4ba3fd94d4276b536e2958c7a575e00b"

    # For database access
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'moodle_user',
        'password': 'password',
        'database': 'moodle_db'
    }
    
    # Initialize services
    # Option 1: Web Service
    moodle_service = MoodleDataService(MOODLE_URL, WEB_SERVICE_TOKEN)
    
    # Option 2: Direct Database
    # moodle_db = MoodleDirectDBService(DB_CONFIG)
    # moodle_db.connect()
    
    # Create data processor
    processor = LocalDataProcessor(moodle_service)
    
    # Example: Analyze user activity
    user_analysis = processor.analyze_user_activity()
    print("User Activity Analysis:", user_analysis)
    
    # Example: Identify at-risk students
    at_risk = processor.identify_at_risk_students()
    print("At-risk students:", len(at_risk))
    
    # Example: Get specific user data
    users = moodle_service.get_all_users()
    if users:
        print(f"Found {len(users)} users")
        
        # Create DataFrame for analysis
        df = processor.create_user_dataframe()
        print("User DataFrame shape:", df.shape)
        print("Columns:", df.columns.tolist())