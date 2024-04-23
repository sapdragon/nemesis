using Microsoft.EntityFrameworkCore;
using Server.Domain.Entities;
using Server.Domain.Interfaces;
using Server.Infrastructure.Data;

namespace Server.Infrastructure.Repositories
{
    public class GameAccountRepository : IGameAccountRepository
    {
        private readonly DatabaseContext _context;
        public GameAccountRepository(DatabaseContext context)
        {
            _context = context;
        }

        public async Task AddSteamAccountAsync(SteamAccount steamAccount)
        {
            await _context.SteamAccounts.AddAsync(steamAccount);
            await _context.SaveChangesAsync();
        }

        public async Task DeleteSteamAccountAsync(SteamAccount steamAccount)
        {
            _context.SteamAccounts.Remove(steamAccount);
            await _context.SaveChangesAsync();
        }

        public async Task<IEnumerable<SteamAccount>> GetAllSteamAccountsAsync()
        {
            return await _context.SteamAccounts.ToListAsync();
        }

        public async Task<SteamAccount> GetSteamAccountByIdAsync(int id)
        {
            return await _context.SteamAccounts.FindAsync(id);
        }

        public async Task<IEnumerable<SteamAccount>> GetSteamAccountsByUserIdAsync(int userId)
        {
            return await _context.SteamAccounts.Where(steamAccount => steamAccount.UserId == userId).ToListAsync();
        }

        public async Task UpdateSteamAccountAsync(SteamAccount steamAccount)
        {
            _context.Entry(steamAccount).State = EntityState.Modified;
            await _context.SaveChangesAsync();
        }
    }
}
