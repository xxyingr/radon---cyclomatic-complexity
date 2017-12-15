from flask import Flask
from flask_restful import Resource, Api, reqparse
import json, requests, time, getpass


app = Flask(__name__)
api = Api(app)

class getRepo(Resource):
    def __init__(self):  # Upon initialisation of the class          
        self.manager = manager  # Init the global manager
        self.reqparser = reqparse.RequestParser()

        # For every value coming in JSON, you need an argument
        self.reqparser.add_argument('pullStatus', type=int, location = 'json')  # Repeat for multiple variables
        self.reqparser.add_argument('complexity', type=float, location='json')

    def get(self):
        args = self.reqparser.parse_args()
        if args['pullStatus'] == False:  # Repo hasn't been pulled yet
            print("GOT 1")
            return {'repo': 'https://github.com/jrios6/Berkeley-AI-PacMan-Lab-1'}  
        if args['pullStatus'] == True:  # Repo has been pulled, can now increment
            self.manager.currNumWorkers += 1
            if self.manager.currNumWorkers == self.manager.numWorkers:
                self.manager.startTime = time.time()  # Start the timer
            print("WORKER NUMBER: {}".format(self.manager.currNumWorkers))
    def post(self):
        pass

api.add_resource(getRepo, "/repo", endpoint="repo")


#  API for obtaining commits and posting the cyclomatic results
class cycComplexity(Resource):
    def __init__(self):  # Upon initialisation of the class
        self.manager = manager  # Init the global manager
        super(cycComplexity, self).__init__()  # Initialising the Resource class
        self.reqparser = reqparse.RequestParser()

        # For every value coming in JSON, you need an argument
        self.reqparser.add_argument('commit', type=str, location = 'json')  # Repeat for multiple variables
        self.reqparser.add_argument('complexity', type=float, location='json')
        # self.reqparser.add_argument('version', type=int, location='json')

    def get(self):
        if self.manager.currNumWorkers < self.manager.numWorkers: # still waiting on workers
            time.sleep(0.1)
            return {'sha': -2}
        if len(self.manager.commitList) == 0:  # No more commits to give
            return {'sha': -1}
        commitValue = self.manager.commitList[0]  # give next commit in list
        del self.manager.commitList[0]  # Remove item from list of commits to compute
        print(commitSha)
        return {'sha':commitValue}


    def post(self):
        self.manager.listOfCCs.append({'sha':args['commitSha'], 'complexity':args['complexity']})
        print(self.reqparser.parse_args())
        args = self.reqparser.parse_args()
        if len(self.manager.listOfCCs) == self.manager.totalNumberOfCommits:
            endTime = time.time() - self.manager.startTime
            totalAverageCC = 0
            for x in self.manager.listOfCCs:
                if x['complexity'] > 0:
                    totalAverageCC += x['complexity']
                else:
                    print("Commit {} has no computable files".format(x['sha']))
            totalAverageCC = totalAverageCC / len(self.manager.listOfCCs)
            print("OVERALL CYCLOMATIC COMPLEXITY FOR REPOSITORY: {}".format(totalAverageCC))
        return {'success':True}

#  Created a route at /cyclomatic with an endpoint called cyclomatic
api.add_resource(cycComplexity, "/cyclomatic", endpoint="cyclomatic")


class managerServer():
    def __init__(self):
        self.numWorkers = int(input("Enter number of worker nodes: "))
        
        self.currNumWorkers = 0  # Number of workers who have connected to the manager
        self.startTime = 0.0  # Start time for the timer
        
        currentpage = 1
        self.commitList = []
        morePage = True
        while morePage:
            commitURL = 'https://api.github.com/repos/jrios6/Berkeley-AI-PacMan-Lab-1/commits?page=' + str(currentpage) + '&per_page=100'
            response = requests.get(commitURL)
            data = json.loads(response.text)
            if len(data) < 2:
                morePage = False
                print('No more pages.')
            else:
                for d in data:
                    self.commitList.append(d['sha'])
                    print('Commit Sha:', str(d['sha']))
                currentpage += 1

        self.commitNum = len(self.commitList)
        self.complexityList = []
        print('Total number of commits is: ', str(self.commitNum))


if __name__ == "__main__":
    manager = managerServer()
    app.run(port=5000) 