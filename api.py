from flask import Flask
from flask_restful import Resource, Api,reqparse,abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///sqlite.db'
db = SQLAlchemy(app)

class ToDoModel(db.Model):
    # 3 things
    id = db.Column(db.Integer,primary_key=True)
    task = db.Column(db.String(200))
    summary = db.Column(db.String(500))
with app.app_context():
    db.create_all()

class HelloWorld(Resource):
    def get(self): #get api
        return {
            'data': 'Hello, World!'
        }
class HelloName(Resource):
     def get(self,name):
         return {
             'data': 'Hello,{}'.format(name)
         }

# 2 endpoints
# /todos endpoint /todos/1/2/3/4/5
# write endpoints using add_resource
api.add_resource(HelloWorld,'/helloworld')
api.add_resource(HelloName,'/helloworld/<string:name>')
# for every endpoint you need a class
# get localhost:5000/helloworld
#Hello, World!

'''todos = {
    1:{"task":"Write Hello World Program","summary":"write the code using python."}
    ,2:{"task":"Task2", "summary":"writing task2"}
    ,3:{"task":"Task2", "summary":"writing task2"}

}'''

# How are we going to return our data, make sure it is serializable, we are going to mock that way of writing dictionaries by essentialy
# Having Resource fields
task_post_args = reqparse.RequestParser()
task_post_args.add_argument("task",type=str,help="Task is required",required=True)
task_post_args.add_argument("summary",type=str,help="Summary is required",required=True)

task_update_args = reqparse.RequestParser()
task_update_args.add_argument("task",type=str)
task_update_args.add_argument("summary",type=str)

resource_fields = {
    'id':fields.Integer,
    'task':fields.String,
    'summary':fields.String,
}
# annotate with marshal_with

class ToDoList(Resource):
    def get(self):
        tasks = ToDoModel.query.all()
        todos = {}
        for task in tasks:
            todos[task.id] = {"task":task.task,"summary":task.summary}
        return todos
api.add_resource(ToDoList,'/todos')

class ToDo(Resource):
    @marshal_with(resource_fields)
    def get(self,todo_id):
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404,message="Could not find task with that id")
        return task
    @marshal_with(resource_fields)
    def post(self,todo_id):
        args = task_post_args.parse_args()
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if task: # if task present in the database then abort, can't add to an existing todo_id
            abort(409,"Task ID already taken")
        # Create new object to be added in the database
        new_todo = ToDoModel(id=todo_id,task=args['task'],summary=args['summary'])
        db.session.add(new_todo)
        db.session.commit()
        return new_todo, 201

    @marshal_with(resource_fields)
    def put(self,todo_id):

        args = task_update_args.parse_args()
        task_found = ToDoModel.query.filter_by(id=todo_id).first()

        if not task_found:
            abort(404,message="Task doesn't exist, cannot update")
        if args['task']:
            task_found.task = args["task"]
        if args['summary']:
            task_found.summary = args['summary']
        db.session.commit()
        return task_found
    def delete(self,todo_id):
        task = ToDoModel.query.filter_by(id=todo_id).first()
        db.session.delete(task)
        db.session.commit()
        return 'Todo Deleted',204

# We need api Endpoints which is going to be a class in itself
api.add_resource(ToDo,'/todos/<int:todo_id>')
#put will be in json format
# we need to parse the data
# We will use reqparse for this purpose
if __name__ == '__main__':
    app.run(debug=True)