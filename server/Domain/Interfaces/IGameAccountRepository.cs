using Server.Domain.Entities;

namespace Server.Domain.Interfaces
{
    public interface IGameAccountRepository
    {
        Task<SteamAccount> GetSteamAccountByIdAsync(int id);

        Task<IEnumerable<SteamAccount>> GetAllSteamAccountsAsync();
        Task<IEnumerable<SteamAccount>> GetSteamAccountsByUserIdAsync(int userId);

        Task AddSteamAccountAsync(SteamAccount steamAccount);
        Task UpdateSteamAccountAsync(SteamAccount steamAccount);
        Task DeleteSteamAccountAsync(SteamAccount steamAccount);
    }
}
