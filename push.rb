require 'houston'
require 'optparse'

# Environment variables are automatically read, or can be overridden by any specified options. You can also
# conveniently use `Houston::Client.development` or `Houston::Client.production`.
APN = Houston::Client.development
APN.certificate = File.read("./Apple Push.pem")

# An example of the token sent back when a device registers for notifications

# Create a notification that alerts a message to the user, plays a sound, and sets the badge on the app

#args = Hash[ ARGV.join(' ').scan(/--?([^=\s]+)(?:=(\S+))?/) ]


options = {}
OptionParser.new do |opt|
  opt.on('--title TITLE') { |o| options[:title] = o }
  opt.on('--body BODY') { |o| options[:body] = o }
  opt.on('--token TOKEN') { |o| options[:token] = o }
end.parse!

token = options[:token]

notification = Houston::Notification.new(device: token)
notification.alert = { "title" => options[:title], "body" => options[:body] }

# Notifications can also change the badge count, have a custom sound, have a category identifier, indicate available Newsstand content, or pass along arbitrary data.
#notification.badge = 57
notification.sound = "default"
#notification.category = "INVITE_CATEGORY"
#notification.content_available = true
#notification.custom_data = {foo: "bar"}

# And... sent! That's all it takes.
APN.push(notification)
