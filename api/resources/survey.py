from flask import jsonify, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import current_user

from models.survey import Survey
from models.user import User
from models.question import Question, ScaleQuestion, OpenAnswerQuestion, MultipleChoiceQuestion, AnswerOption


def is_allowed(user):
    return user.isActivated and not user.isBlocked


class AddSurvey(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        current_user_id = get_jwt_identity()
        if not is_allowed(User.find_by_id(current_user_id)):
            return {'message': 'User is not allowed to perform this action.'}, 400
        try:
            config = data['config']
            data = data['data']
            exists = False
            if 'id' in data:
                survey = Survey.get_survey(data['id'])
                if not survey.surveyOwner == current_user_id:
                    return {'message': 'User is not the owner of this survey.'}, 400
                exists = True
            else:
                survey = Survey(current_user_id, data['title'], data['description'], config['startDate'], config['endDate'])
            if exists:
                survey.modify(data['title'], data['description'], config['startDate'], config['endDate'])
                for question in survey.questions:
                    question.delete_question()
            survey.add_survey()
            questions = data['formBuilder']['list']
            for i, question in enumerate(questions):
                options = question['options']
                model_key = question['key']
                model = question['model']
                if isinstance(options, dict) and 'tag' in options:
                    base_question = Question(survey.id, question['title'],
                                             question['order'], tag=options['tag'],
                                             model_key=model_key, model=model)
                    base_question.add_question()
                else:
                    type = question['type']
                    base_question = Question(survey.id, question['title'], question['order'],
                                             description=question['description'],
                                             model_key=model_key, model=model)
                    base_question.add_question()
                    if type == 'slider':
                        scale_question = ScaleQuestion(base_question.id, options['min'], options['max'])
                        scale_question.add_question()
                    elif type == 'checkbox' or type == 'radio':
                        allow_multiple_answers = True if type == 'checkbox' else False
                        multiple_choice_question = MultipleChoiceQuestion(base_question.id, allow_multiple_answers)
                        multiple_choice_question.add_question()
                        answers = options['options']
                        for answer in answers:
                            answer_option = AnswerOption(multiple_choice_question.id, answer['text'])
                            answer_option.add_answer()
                    elif type == 'input':
                        open_answer_question = OpenAnswerQuestion(base_question.id)
                        open_answer_question.add_question()
        except KeyError:
            return {'message': 'Invalid data in post request.'}, 400
        if exists:
            return {'message': 'The survey {} has been modified.'.format(survey.title)}, 200
        return {'message': 'The survey {} has been created.'.format(survey.title)}, 200


class ListSurveysByUser(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        surveys = Survey.list_surveys_by_user(current_user_id)
        return jsonify([survey.serialize() for survey in surveys])


class GetSurvey(Resource):
    @jwt_required(optional=True)
    def get(self, survey_id):
        allow = True
        survey = Survey.get_survey(survey_id)
        if not survey:
            return {'message': 'Such survey does not exist.'}, 403
        try:
            current_user_id = get_jwt_identity()
            if current_user_id is not None:
                if not is_allowed(User.find_by_id(current_user_id)):
                    return {'message': 'You are not allowed to access the website.'}, 403
                if survey.surveyOwner == current_user_id:
                    allow = True
        except Exception as e:
            allow = False
        if not allow:
            return {'message': 'You are not allowed to access this survey.'}, 403
        return jsonify(survey.get_json())
