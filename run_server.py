import Queue
from multiprocessing.managers import SyncManager
import multiprocessing
import time

PORTNUM = 5000
AUTHKEY = "abc"

def make_nums(N):
    """ Create N large numbers to factorize.
    """
    nums = [999999999999]
    for i in xrange(N):
        nums.append(nums[-1] + 2)
    return nums

# This is based on the examples in the official docs of multiprocessing.
# get_{job|result}_q return synchronized proxies for the actual Queue
# objects.
class JobQueueManager(SyncManager):
    pass

job_q = Queue.Queue()
result_q = Queue.Queue()
#batchId = multiprocessing.Value('i',0)
batchId = None
entier = 0

def get_job_q():
    return job_q

def get_result_q():
    return result_q

def get_batchId():
    import traceback
    traceback.print_stack()
    print "hello world"
    return batchId

def get_entier():
    return entier

def make_server_manager(port, authkey):
    """ Create a manager for the server, listening on the given port.
        Return a manager object with get_job_q and get_result_q methods.
    """

    JobQueueManager.register('get_job_q', callable=get_job_q)
    JobQueueManager.register('get_result_q', callable=get_result_q)
    JobQueueManager.register('get_batchId', callable = get_batchId)
    JobQueueManager.register('get_entier', callable = get_entier)

    manager = JobQueueManager(address=('192.168.0.178', port), authkey=authkey)
    manager.start()
    print 'Server started at port %s' % port
    
    global batchId
    batchId = manager.Value('i', 0)
    
    return manager

def runserver():
    # Start a shared manager server and access its queues
    manager = make_server_manager(PORTNUM, AUTHKEY)
    shared_job_q = manager.get_job_q()
    shared_result_q = manager.get_result_q()
    b = manager.get_batchId()
    b_id = b._getvalue()
    
    entier = manager.get_entier()
    e = entier._getvalue()
    
    print e
    print entier
    
    entier+=1
    
    e+=1
    
    print e
    
    global batchId
    print "batchId",batchId.value
    print "b_id", b_id.value
    N = 999
    nums = make_nums(N)

    # The numbers are split into chunks. Each chunk is pushed into the job
    # queue.
    chunksize = 43
    for i in range(0, len(nums), chunksize):
        shared_job_q.put(nums[i:i + chunksize])

    # Wait until all results are ready in shared_result_q
    numresults = 0
    resultdict = {}
    while numresults < N:
        outdict = shared_result_q.get()
        resultdict.update(outdict)
        numresults += len(outdict)

    # Sleep a bit before shutting down the server - to give clients time to
    # realize the job queue is empty and exit in an orderly way.
    time.sleep(2)
    manager.shutdown()
    return resultdict
    
if __name__=='__main__':
    runserver()