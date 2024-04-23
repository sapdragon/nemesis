namespace Server.Domain.Entities
{
    public class User
    {
        public int Id { get; set; }
        public List<SteamAccount> SteamAccounts { get; set; }
        //public ulong SteamId { get; set; }
        public bool IsBanned { get; set; }
        public string BanReason { get; set; }

        public HardwareInfo hardwareInfo;
    }

}
