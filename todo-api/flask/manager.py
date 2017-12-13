from flask import Flask
from flask_restful import Resource, Api, reqparse
import json, requests, time, getpass


app = Flask(__name__)
api = Api(app)

class getRepo(Resource):
    def __init__(self):  # Upon initialisation of the class          
        self.manager = manager  # Init the global manager
        super(getRepo, self).__init__()  # Initialising the Resource class
        self.reqparser = reqparse.RequestParser()

        # For every value coming in JSON, you need an argument
        self.reqparser.add_argument('pullStatus', type=int, location = 'json')  # Repeat for multiple variables
        self.reqparser.add_argument('complexity', type=float, location='json')

    def get(self):
        args = self.reqparser.parse_args()
        if args['pullStatus'] == False:  # Repo hasn't been pulled yet
            print("GOT 1")
            return {'repo': "https://github.com/{}/{}".format(self.manager.owner, self.manager.repo)}  
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
        global manager  # Init the global manager
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
        print("Sent: {}".format(commitValue))
        return {'sha':commitValue}


    def post(self):
        args = self.reqparser.parse_args()  # parse the arguments from the POST
        print("Received sha {}".format(args['commitSha']))
        print("Received complexity {}".format(args['complexity']))
        self.manager.listOfCCs.append({'sha':args['commitSha'], 'complexity':args['complexity']})
        print(self.manager.listOfCCs)
        print(self.manager.commitList)
        if len(self.manager.listOfCCs) == self.manager.totalNumberOfCommits:
            endTime = time.time() - self.manager.startTime
            print("finished in {} seconds".format(endTime))
            print(len(self.manager.listOfCCs))
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
        self.numWorkers = input("Enter number of worker nodes: ")
        # self.repoDirectory = input("Enter the URL for the repository")
        self.numWorkers = int(self.numWorkers)
        self.currNumWorkers = 0  # Number of workers who have connected to the manager
        self.startTime = 0.0  # Start time for the timer
        # request repository info using the github API
        print("Authenticated Github API requests have a rate limit of 5000 per hour to the Github API")
        print("Unauthenticated requests have a limit of 60 requests per hour")
        idgit = input("Type your Github username to use authenticated requests, or press return to use unauthenitcated requests: ")
        print(len(idgit))
        if len(idgit) != 0:
            gitPassword = getpass.getpass("Type your Github password (input is hidden): ")
        morePages = True  # Loop control variable to check if more pages on github API
        currentPage = 1  # Current page of github API repo info
        self.commitList = []  # List containing all commit sha values
        while morePages:
            if len(idgit) == 0:
                r = requests.get("https://api.github.com/repos/{}/{}/commits?page={}&per_page=100".format(currentPage))  
            else:
                r = requests.get("https://api.github.com/repos/{}/{}/commits?page={}&per_page=100".format(currentPage), auth=(idgit, gitPassword))
            json_data = json.loads(r.text)
            if len(json_data) < 2:
                morePages = False
                print("All pages iterated through")
            else:
                for x in json_data:
                    self.commitList.append(x['sha'])
                    print("Commit Sha: {}".format(x['sha']))
                print("\n")
                currentPage += 1
        self.totalNumberOfCommits = len(self.commitList)  # Total number of commits in repo
        self.listOfCCs = []
        print("Number of commits: {}".format(self.totalNumberOfCommits))


if __name__ == "__main__":
    manager = managerServer()  # ini an instance of managerServer()
    app.run(port=5000)  # int(sys.argv[1])  , debug=True