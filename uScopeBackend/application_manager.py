from flask import current_app, Blueprint, jsonify
from flask_restful import Api, Resource


############################################################
#                      IMPLEMENTATION                      #
############################################################




application_manager_bp = Blueprint('application_manager', __name__, url_prefix='/application')

api = Api(application_manager_bp)


class Application_list(Resource):
    def get(self):
        return jsonify(current_app.applicationManager.applications_list)


class Application_specs(Resource):
    def get(self,name):
        return jsonify(current_app.applicationManager.get_application(name))


api.add_resource(Application_list, '/list')
api.add_resource(Application_specs, '/specs')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class ApplicationManager:
    def __init__(self):
        self.applications, self.applications_list = self.load_applications()

    @staticmethod
    def load_applications():
        settings = [f for f in os.listdir('static') if os.path.isfile(os.path.join('static', f))]
        for fname in settings:
            if not fname.split('.')[1] == 'json':
                continue
            else:
                name = fname.replace('.json', '')

            parsed = name.rsplit('_', 1)

            if parsed[1] == 'descriptor':
                with open('static/'+fname,'r') as f:
                    content = json.load(f)
                    application_specs[content['name']] = content

        for i in application_specs:
            application_list.append(i)

        return application_specs, application_list

    def get_application(self, application_name):
        chosen_application = self.applications[application_name]
        self.load_bitstream(application_name)
        return  chosen_application

    def load_bitstream(self, name):
        pass