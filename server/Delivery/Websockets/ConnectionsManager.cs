using Microsoft.AspNetCore;
using Microsoft.AspNetCore.Mvc;
using Server.Application.Interfaces;
using System.Collections.Concurrent;
using System.Net.WebSockets;
using System.Text;

namespace Server.Delivery.Websockets
{

    public class Connection
    {
        public bool IsAuthenticated { get; set; }
        public WebSocket? WebSocket { get; set; } = null;

        public Connection(WebSocket webSocket)
        {
            WebSocket = webSocket;
        }
    }

    public class ConnectionsManager
    {
        private readonly ConcurrentDictionary<int, Connection> _connections = new ConcurrentDictionary<int, Connection>();

        public Connection GetConnection(int userId)
        {
            return _connections.TryGetValue(userId, out var connection) ? connection : null;
        }
        public void AddConnection(int userId, Connection connection)
        {
            _connections.TryAdd(userId, connection);
        }   
        public void RemoveConnection(int userId)
        {
            _connections.TryRemove(userId, out _);
        }

        public List<int> GetOnlineUsers()
        {
            return _connections.Keys.ToList();
        }

    }

    [Route("/")]
    [EndpointGroupName("websockets")]
    [ApiController]
    public class WebsocketsController : ControllerBase
    {
        private ConnectionsManager _connectionsManager;

        public WebsocketsController()
        {
            _connectionsManager = new ConnectionsManager();
        }


        [HttpGet]
        public async Task<IActionResult> GetAsync()
        {
            if (HttpContext.WebSockets.IsWebSocketRequest)
            {
                var webSocket = await HttpContext.WebSockets.AcceptWebSocketAsync();
                var connection = new Connection(webSocket);
                connection.WebSocket = webSocket;
                _ = connection.WebSocket.SendAsync(new ArraySegment<byte>(Encoding.UTF8.GetBytes("Hello!")), WebSocketMessageType.Text, true, CancellationToken.None);

                return new EmptyResult();
            }

            return new BadRequestResult();
        }
    }
}
