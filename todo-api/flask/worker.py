import json, requests, subprocess

def work():
    
    masterURL = 'http://127.0.0.1:5000/' 
    r = requests.get(masterURL, json={'pullStatus': False})
    data = json.loads(r.text)
    repoURL = data['workerData']
    bashCommand = "cd pulledRepo &" \
                  "rm -rf .git/ &" \
                  "git init &" \
                  "git remote add origin {} &" \
                  "git branch --set-upstream-to=origin/<branch> master & " \
                  "git pull".format(repoUrl)
    subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    r = requests.get(masterURL, json={'pullStatus': True})

    
    mCommits = True
    while mCommits:
        r = requests.get("http://127.0.0.1:5000/cyclomatic")
        data = json.loads(r.text)
        print(data)
        hsha = data['sha']
        print("Received: ", str(hsha))
        if hsha == -2:  # Polling for manager to start giving commits
           print("Waiting")
        else:
            if hsha == -1:
                print("No more items")
                break
            bashCommand = "cd pulledRepo &" \
                          "git reset --hard {}".format(hsha)
            subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            cmd = "radon cc -a -s workerData"
            output = subprocess.check_output(cmd).decode()
            print(output)

            numCommitsDone = 0
            aveCC = result.rfind('(')
            if output.find("ERROR") != -1: 
                r = requests.post("http://127.0.0.1:5000/cyclomatic",
                                  json={'commit': hsha, 'complexity': 0})
            if output[aveCC + 1:-2] == "":
                print("NO RELEVENT FILES")
                r = requests.post("http://127.0.0.1:5000/complexity",
                                  json={'commit': hsha, 'complexity': -1})
            else:
                u = output[result.rfind('(') + 1:-2].replace(')', '').replace('\r', '').replace('\n', '').replace('"', '')
                if u is None:
                    r = requests.post('http://127.0.0.1:5000/cyclomatic',
                                         json={'commit': hsha, 'complexity': 0})
                else: 
                    aveCC = float(u)
                    r = requests.post('http://127.0.0.1:5000/cyclomatic',
                                         json={'commit': hsha, 'complexity': aveCC})

            numCommitsDone += 1  # Increment the number of commits this node has completed
    print("Completed having computed {} commits (including non-computable commits)".format(numCommitsDone))
