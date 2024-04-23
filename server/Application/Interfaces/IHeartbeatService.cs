using Server.Application.DTOs;

namespace Server.Application.Interfaces
{
    public interface IHeartbeatService
    {
        (string token, int userId) Authenticate(InitialHeartbeatDto inputInitialHeartbeat);
    }
}
