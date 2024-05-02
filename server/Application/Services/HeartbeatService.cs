using Server.Application.DTOs;
using Server.Application.Interfaces;
using Server.Domain.Interfaces;

namespace Server.Application.Services
{
    public class HeartbeatService : IHeartbeatService
    {
        private readonly IUserRepository _userRepository;

        public HeartbeatService(IUserRepository userRepository)
        {
            _userRepository = userRepository;
        }

        public (string token, int userId) Authenticate(InitialHeartbeatDtoRequest inputInitialHeartbeat)
        {
            throw new NotImplementedException();
        }
    }
}
