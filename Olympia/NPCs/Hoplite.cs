using Microsoft.Xna.Framework;
using Terraria;
using Terraria.Audio;
using Terraria.GameContent.ItemDropRules;
using Terraria.ID;
using Terraria.ModLoader;

namespace Olympia.NPCs
{
    public class Hoplite : ModNPC
    {
        public override void SetStaticDefaults()
        {
            Main.npcFrameCount[Type] = 3;
        }

        public override void SetDefaults()
        {
            NPC.width = 36;
            NPC.height = 52;
            NPC.damage = 24;
            NPC.defense = 8;
            NPC.lifeMax = 80;
            NPC.HitSound = SoundID.NPCHit1;
            NPC.DeathSound = SoundID.NPCDeath1;
            NPC.knockBackResist = 0.4f;
            NPC.value = 150.0f;
            NPC.aiStyle = NPCAIStyleID.Fighter;
            AIType = NPCID.Zombie;
            AnimationType = NPCID.Zombie;
        }

        public override float SpawnChance(NPCSpawnInfo spawnInfo)
        {
            if (Systems.OlympiaWorld.InArea(spawnInfo.Player, Systems.OlympiaWorld.TempleOfOlympusArea))
            {
                return 0.6f;
            }
            return spawnInfo.Player.ZoneOverworldHeight ? 0.03f : 0f;
        }

        public override void ModifyNPCLoot(NPCLoot npcLoot)
        {
            npcLoot.Add(ItemDropRule.Common(ModContent.ItemType<Items.BronzeBar>(), 3, 1, 3));
        }
    }
}
