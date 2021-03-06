import sched, time, threading, datetime
import pytumblr
import TumblrAngelAnalyzer as sentiment
import alert as alert
from nested_lookup import nested_lookup

class Analyzer(object):
	userData = []
	done_analyzing = False
	current_status = "neu"
	blogToWatch = ''
	client = ""
	CHECKING_INTERVAL = 15
	POST_THRESHOLD = 3
	
	def __init__(self, blogToWatch):
		self.userData = []
		self.done_analyzing = False
		self.current_status = "neu"
		self.blogToWatch = blogToWatch
		self.client = pytumblr.TumblrRestClient(

		)
		
	# Returns the current sentiment of the last three posts of a tumblr account
	def getBlogDetails(self):

		data = self.client.posts(self.blogToWatch + '.tumblr.com', limit=self.POST_THRESHOLD, filter='text')

		working_data = []
		#print(data)
		tags = nested_lookup('tags', data['posts'])
		bodies = nested_lookup('body', data['posts'])
		conversations = nested_lookup('conversation', data['posts'])
		dates = nested_lookup('date', data['posts'])

		for item in tags:
			for data in item:
				working_data.append(data)
				
		for item in bodies:
			working_data.append(item)

		for item in conversations:
			working_data.append(item)	
			
		working_data = list(filter(None, working_data))
		
		return " ".join(working_data)
		
	def logTimeAndStatus(self):
		now = datetime.datetime.now()
		timeAndDate = '[' + now.strftime("%Y-%m-%d %H:%M") + ']'
		print(timeAndDate + self.blogToWatch + ': ' + self.current_status)
		
	# Gets the status of the
	def updateStatus(self):
		starttime=time.time()
		try:
			while(True):
				self.current_status = sentiment.getSentiment(self.getBlogDetails())
				self.logTimeAndStatus()
				if self.current_status == 'neg':
					alert.alertUser(self.blogToWatch)
					break
				else:
					time.sleep(self.CHECKING_INTERVAL - ((time.time() - starttime) % self.CHECKING_INTERVAL))
		except KeyboardInterrupt:
			sys.exit(1)
		
	def start(self):
		t = threading.Thread(target=self.updateStatus)
		t.start()
		
