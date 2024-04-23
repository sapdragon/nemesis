namespace Server.Domain.Entities
{
    public class SteamAccount
    {
        public int Id { get; set; }
        public ulong SteamId { get; set; }
        public DateTime LastActive { get; set; }

        public int UserId { get; set; }
        public User User { get; set; }
    }
}
