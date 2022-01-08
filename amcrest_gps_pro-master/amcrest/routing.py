from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from django.conf.urls import url
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from listener.consumers import ObdConsumer


application = ProtocolTypeRouter({
	'websocket':AllowedHostsOriginValidator(
		URLRouter(
				[
					url(r"^udp/(?P<imei>[\w.@+-]+)/$", ObdConsumer),
				]
			)
		),
	'channel': ChannelNameRouter({"game_engine": ObdConsumer}),
	},
	

	)