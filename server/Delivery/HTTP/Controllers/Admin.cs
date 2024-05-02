using Microsoft.AspNetCore.Mvc;
using Server.Domain.Interfaces;

namespace Server.Delivery.HTTP.Controllers
{
    [Route("api/v1/admin/[controller]")]
    [ApiController]
    [EndpointGroupName("http")]
    public class AdminController : ControllerBase
    {
        private readonly IUserRepository _userRepository;
        private readonly IConfiguration _configuration;

        public AdminController(IUserRepository userRepository, IConfiguration configuration)
        {
            _userRepository = userRepository;
            _configuration = configuration;
        }

        // GET: api/v1/admin/users
        [HttpPost("users")]
        public async Task<IActionResult> GetUsers()
        {
            // get login password from request
            var login = Request.Headers["login"];
            var password = Request.Headers["password"];

            if (login != _configuration["AdminLogin"] || password != _configuration["AdminPassword"])
                return Unauthorized();
            
            var users = await _userRepository.GetAllUsersAsync();
            return Ok(users);
        }

        // POST: api/v1/admin/ban
        [HttpPost("ban")]
        public async Task<IActionResult> BanUser([FromBody] int userId)
        {
            // get login password from request
            var login = Request.Headers["login"];
            var password = Request.Headers["password"];

            if (login != _configuration["AdminLogin"] || password != _configuration["AdminPassword"])
                return Unauthorized();

            var user = await _userRepository.GetUserByIdAsync(userId);
            if (user == null)
                return NotFound();

            user.IsBanned = true;
            await _userRepository.UpdateUserAsync(user);
            return Ok();
        }

        // POST: api/v1/admin/unban
        [HttpPost("unban")]
        public async Task<IActionResult> UnbanUser([FromBody] int userId)
        {
            // get login password from request
            var login = Request.Headers["login"];
            var password = Request.Headers["password"];

            if (login != _configuration["AdminLogin"] || password != _configuration["AdminPassword"])
                return Unauthorized();

            var user = await _userRepository.GetUserByIdAsync(userId);
            if (user == null)
                return NotFound();

            user.IsBanned = false;
            await _userRepository.UpdateUserAsync(user);
            return Ok();
        }

        // POST: api/v1/admin/user
        [HttpPost("user")]
        public async Task<IActionResult> GetUser([FromBody] int userId)
        {
            // get login password from request
            var login = Request.Headers["login"];
            var password = Request.Headers["password"];

            if (login != _configuration["AdminLogin"] || password != _configuration["AdminPassword"])
                return Unauthorized();

            var user = await _userRepository.GetUserByIdAsync(userId);
            if (user == null)
                return NotFound();

            return Ok(user);
        }

        // POST: api/v1/admin/delete
        [HttpPost("delete")]
        public async Task<IActionResult> DeleteUser([FromBody] int userId)
        {
            // get login password from request
            var login = Request.Headers["login"];
            var password = Request.Headers["password"];

            if (login != _configuration["AdminLogin"] || password != _configuration["AdminPassword"])
                return Unauthorized();

            var user = await _userRepository.GetUserByIdAsync(userId);
            if (user == null)
                return NotFound();

            await _userRepository.DeleteUserAsync(user);
            return Ok();
        }
    }
}
