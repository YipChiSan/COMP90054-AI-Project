import os
import pickle

def generateLayoutFile(replayDir, replayLayoutsDir):
    files= os.listdir(replayDir)

    for file in files:
        if not os.path.isdir(file):
            with open(replayDir+'/'+file, 'rb') as replayFile:
                info = pickle.load(replayFile)
                layout = info['layout']
                actions = info['actions']
                with open(replayLayoutsDir+'/'+file+'.capture.lay', 'w+') as outputFile:
                    outputFile.write(str(layout))
        rerunReplayGame(file, actions)

def rerunReplayGame(replayFileName, actions):
    layoutPath = '.' + replayLayoutsDir + '/' + replayFileName + '.capture.lay'
    # redActions = [action for i, action in enumerate(actions) if not action[0] & 1]
    # blueActions = [action for i, action in enumerate(actions) if action[0] & 1]
    with open('./replayAgentActions','wb') as f:
        f.write(pickle.dumps(actions))

    os.system('python capture.py -l {} -r replayAgent  -b replayAgent'.format(layoutPath))

"""
$ python readReplay.py
"""
if __name__ == '__main__':
    replayDir = './replays'
    replayLayoutsDir = './replayLayouts'
    generateLayoutFile(replayDir, replayLayoutsDir)
