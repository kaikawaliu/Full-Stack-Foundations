from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		try:
			if self.path.endswith("/restaurants"):
				
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				
				output = ""
				output += "<html><body>"
				
				output += "<a href = 'restaurants/new'>Make a New Restaurant Here</a>"
				
				items = session.query(Restaurant).all()
				for item in items:
					output += "<h1>%s</h1>" % item.name
					output += "<a href= 'restaurants/%s/edit'>Edit</a>" % item.id
					output += "</br>"
					output += "<a href= 'restaurants/%s/delete'>Delete</a>" % item.id
					output += "</br>"
				
				
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return
			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				
				output = ""
				output += "<html><body>"
				output += "<h2>Make a New Restaurant</h2>"
				output += '''<form method='POST' enctype='multipart/form-data' 
				action='/restaurants/new'><input name="newRestaurantName" type="text" placeholder
				='New Restaurant Name'><input type="submit" value="Create"></form>'''
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return
			if self.path.endswith("/edit"):
				restaurantID = self.path.split("/")[2]
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				
				tRestaurant = session.query(Restaurant).filter_by(id=restaurantID).one()
				
				output = ""
				output += "<html><body>"
				output += "<h2>%s</h2>" % tRestaurant.name
				output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % restaurantID
				output += "<input name='updateRestaurantName' type='text' placeholder='%s'>" % tRestaurant.name
				output += "<input type='submit' value = 'Rename'>"
				output += "</form>"
				output += "</body></html>"
				
				self.wfile.write(output)
			if self.path.endswith("/delete"):
				restaurantID = self.path.split("/")[2]
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				tRestaurant = session.query(Restaurant).filter_by(id=restaurantID).one()
				output = ""
				output += "<html><body>"
				output += "<h1>Are you sure you want to delete</h1>"
				output += "<h2>%s</h2>" % tRestaurant.name
				output += "<form method='POST' enctype='multipart/form-data' actopm='/restaurants/%s/delete'>" % restaurantID
				output += "<input type='submit' value= 'Delete'>"
				output += "</form>"
				output += "</body></html>"
				
				self.wfile.write(output)
		except IOError:
			self.send_error(404, 'File Not Found: %s' % self.path)
			
	def do_POST(self):
		try:
			if self.path.endswith("restaurants/new"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					newRestaurantName = fields.get('newRestaurantName')
					newRestaurant = Restaurant(name=newRestaurantName[0])
					session.add(newRestaurant)
					session.commit()
				self.send_response(301)
				self.send_header('Content-type','text/html')
				self.send_header('Location','/restaurants')
				self.end_headers()
			if self.path.endswith("/edit"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					updatedRestaurantName = fields.get('updateRestaurantName')
					restaurantID = self.path.split("/")[2]
					
					myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantID).one()
					if myRestaurantQuery != []:
						myRestaurantQuery.name = updatedRestaurantName[0]
						session.add(myRestaurantQuery)
						session.commit()
						self.send_response(301)
						self.send_header('Content-type','text/html')
						self.send_header('Location','/restaurants')
						self.end_headers()
			if self.path.endswith("/delete"):
					deleteRestaurantID = self.path.split("/")[2]
					myRestaurantQuery = session.query(Restaurant).filter_by(id=deleteRestaurantID).one()
					if myRestaurantQuery != []:
						session.delete(myRestaurantQuery)
						session.commit()
						self.send_response(301)
						self.send_header('Content-type','text/html')
						self.send_header('Location','/restaurants')
						self.end_headers()
		except:
			pass
def main():
	try:
		port = 8080
		server = HTTPServer(('',port),webServerHandler)
		print "WebServer running on port %s" % port
		server.serve_forever()
	except KeyboardInterrupt:
		print " ^C entered, stopping web server...."
		server.socket.close()
		
if __name__ == '__main__':
	main()
