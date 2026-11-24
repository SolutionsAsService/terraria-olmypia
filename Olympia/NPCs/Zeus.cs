using Microsoft.Xna.Framework;
using Terraria;
using Terraria.Audio;
using Terraria.GameContent.ItemDropRules;
using Terraria.ID;
using Terraria.ModLoader;

namespace Olympia.NPCs
{
    [AutoloadBossHead]
    public class Zeus : ModNPC
    {
        private int hoverTimer;

        public override void SetStaticDefaults()
        {
            Main.npcFrameCount[Type] = 4;
            NPCID.Sets.MPAllowedEnemies[Type] = true;
        }

        public override void SetDefaults()
        {
            NPC.width = 130;
            NPC.height = 150;
            NPC.damage = 120;
            NPC.defense = 34;
            NPC.lifeMax = 46000;
            NPC.HitSound = SoundID.NPCHit54;
            NPC.DeathSound = SoundID.NPCDeath6;
            NPC.knockBackResist = 0f;
            NPC.value = Item.buyPrice(gold: 30);
            NPC.aiStyle = -1;
            NPC.noGravity = true;
            NPC.noTileCollide = true;
            NPC.boss = true;
            NPC.npcSlots = 10f;
            NPC.lavaImmune = true;
            Music = MusicID.LunarBoss;
        }

        public override void ApplyDifficultyAndPlayerScaling(int numPlayers, float balance, float bossAdjustment)
        {
            NPC.lifeMax = (int)(NPC.lifeMax * 0.75f * bossAdjustment);
            NPC.damage = (int)(NPC.damage * 0.75f);
        }

        private void ToHover()
        {
            NPC.ai[0] = 0f;
            NPC.ai[1] = 0f;
            NPC.ai[2] = 0f;
            hoverTimer = 0;
        }

        public override void AI()
        {
            NPC.TargetClosest(true);
            Player target = Main.player[NPC.target];
            if (!target.active || target.dead)
            {
                NPC.velocity.Y -= 0.4f;
                NPC.EncourageDespawn(60);
                return;
            }
            bool enraged = NPC.life < NPC.lifeMax * 0.5f;
            int dir = target.Center.X > NPC.Center.X ? 1 : -1;
            ref float state = ref NPC.ai[0];
            ref float timer = ref NPC.ai[1];
            ref float count = ref NPC.ai[2];
            timer++;
            NPC.spriteDirection = dir;
            switch ((int)state)
            {
                default:
                case 0: // hover above the player, then choose an attack
                {
                    hoverTimer++;
                    float side = (float)System.Math.Sin(hoverTimer * 0.02f) * 320f;
                    Vector2 home = target.Center + new Vector2(side, -300f);
                    Vector2 desired = (home - NPC.Center).SafeNormalize(Vector2.Zero) * 13.0f * (enraged ? 1.3f : 1f);
                    NPC.velocity = Vector2.Lerp(NPC.velocity, desired, 0.06f);
                    if (timer > (enraged ? 70f : 110f))
                    {
                        timer = 0f;
                        count = 0f;
                        switch (Main.rand.Next(4))
                        {
                            case 0: state = 1f; break; case 1: state = 2f; break; case 2: state = 3f; break; case 3: state = 4f; break;
                        }
                    }
                    break;
                }
                case 1: // a dash: passes at the player, each telegraphed
                {
                    if (timer < 30f)
                    {
                        NPC.velocity *= 0.9f;
                    }
                    else if (timer == 30f)
                    {
                        NPC.velocity = (target.Center - NPC.Center).SafeNormalize(Vector2.UnitY) * 22.0f * (enraged ? 1.25f : 1f);
                        SoundEngine.PlaySound(SoundID.Roar, NPC.Center);
                    }
                    else if (timer > 56f)
                    {
                        count++;
                        timer = 0f;
                        if (count >= 4f)
                        {
                            ToHover();
                        }
                    }
                    break;
                }
                case 2: // a volley: a fan of bolts from the front
                {
                    NPC.velocity *= 0.92f;
                    if (timer % 14f == 0f && Main.netMode != NetmodeID.MultiplayerClient)
                    {
                        Vector2 aim = (target.Center - NPC.Center).SafeNormalize(Vector2.UnitY);
                        int shots = 8 + (enraged ? 2 : 0);
                        for (int i = 0; i < shots; i++)
                        {
                            float spread = ((i - (shots - 1) / 2f) * 0.13f);
                            Vector2 vel = aim.RotatedBy(spread) * 15.0f;
                            Projectile.NewProjectile(NPC.GetSource_FromAI(), NPC.Center, vel, ModContent.ProjectileType<Projectiles.ZeusLightning>(), 88, 0f, Main.myPlayer);
                        }
                        SoundEngine.PlaySound(SoundID.Item20, NPC.Center);
                    }
                    if (timer > 52f)
                    {
                        ToHover();
                    }
                    break;
                }
                case 3: // a summons
                {
                    NPC.velocity.X *= 0.9f;
                    if (timer == 30f && Main.netMode != NetmodeID.MultiplayerClient)
                    {
                        int minions = 4 + (enraged ? 1 : 0);
                        for (int i = 0; i < minions; i++)
                        {
                            NPC.NewNPC(NPC.GetSource_FromAI(), (int)NPC.Center.X + (i - minions / 2) * 40, (int)NPC.Center.Y, ModContent.NPCType<NPCs.StymphalianBird>());
                        }
                        SoundEngine.PlaySound(SoundID.Item8, NPC.Center);
                    }
                    if (timer > 70f)
                    {
                        ToHover();
                    }
                    break;
                }
                case 4: // a rain: bolts falling from above the player, in waves
                {
                    NPC.velocity *= 0.9f;
                    if (timer % 28f == 0f && timer <= 84f && Main.netMode != NetmodeID.MultiplayerClient)
                    {
                        int n = 6 + (enraged ? 2 : 0);
                        for (int i = 0; i < n; i++)
                        {
                            Vector2 at = new Vector2(target.Center.X + (i - n / 2f) * 90.0f + Main.rand.Next(-20, 21), target.Center.Y - 520f);
                            Projectile.NewProjectile(NPC.GetSource_FromAI(), at, new Vector2(0f, 14.0f), ModContent.ProjectileType<Projectiles.ZeusLightning>(), 92, 0f, Main.myPlayer);
                        }
                        SoundEngine.PlaySound(SoundID.Item8, target.Center);
                    }
                    if (timer > 124f)
                    {
                        ToHover();
                    }
                    break;
                }
            }
        }

        public override void FindFrame(int frameHeight)
        {
            NPC.frameCounter++;
            if (NPC.frameCounter > 7)
            {
                NPC.frameCounter = 0;
                NPC.frame.Y = (NPC.frame.Y + frameHeight) % (frameHeight * Main.npcFrameCount[Type]);
            }
        }

        public override void ModifyNPCLoot(NPCLoot npcLoot)
        {
            npcLoot.Add(ItemDropRule.BossBag(ModContent.ItemType<Items.ZeusBag>()));
            LeadingConditionRule notExpert = new LeadingConditionRule(new Conditions.NotExpert());
            notExpert.OnSuccess(ItemDropRule.Common(ModContent.ItemType<Items.CloakOfOlympus>(), 1, 1, 1));
            notExpert.OnSuccess(ItemDropRule.Common(ModContent.ItemType<Items.ThunderboltOfZeus>(), 3, 1, 1));
            notExpert.OnSuccess(ItemDropRule.Common(ModContent.ItemType<Items.TridentOfPoseidon>(), 3, 1, 1));
            notExpert.OnSuccess(ItemDropRule.Common(ModContent.ItemType<Items.LightningFragment>(), 1, 20, 30));
            notExpert.OnSuccess(ItemDropRule.Common(ModContent.ItemType<Items.GorgonScale>(), 1, 10, 16));
            npcLoot.Add(notExpert);
        }

        public override void OnKill()
        {
            Systems.OlympiaWorld.downedZeus = true;
            if (Main.netMode == NetmodeID.Server)
            {
                NetMessage.SendData(MessageID.WorldData);
            }
        }
    }
}
