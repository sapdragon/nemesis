namespace Server.Domain.Entities
{
    public class User
    {
        public int Id { get; set; }
        public ulong SteamId { get; set; }
        public bool IsBanned { get; set; }
        public string? BanReason { get; set; }

    }

}
