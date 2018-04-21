import threading, random

def Splitter(words):
    mylist = words.split()
    newList = []
    while(mylist):
        newList.append(mylist.pop(
            random.randrange(0, len(mylist))))
    print(" ".join(newList))
    
if __name__ == '__main__':
    sentence = "I am a handsome beast. Word."
    numThreads = 5
    threadList = []
    
    print("Starting..")
    for i in range(numThreads):
        t = threading.Thread(target=Splitter, args=(sentence,))
        print""
        t.start()
        threadList.append(t)
        
    print("Thread Count: " + str(threading.activeCount()))
    print("Exiting..")