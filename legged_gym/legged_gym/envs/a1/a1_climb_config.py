from os import path as osp
import numpy as np
from legged_gym.envs.a1.a1_field_config import A1FieldCfg, A1FieldCfgPPO
from legged_gym.utils.helpers import merge_dict

class A1ClimbCfg( A1FieldCfg ):

    #### uncomment this to train non-virtual terrain
    # class sensor( A1FieldCfg.sensor ):
    #     class proprioception( A1FieldCfg.sensor.proprioception ):
    #         delay_action_obs = True
    #         latency_range = [0.04-0.0025, 0.04+0.0075]
    #### uncomment the above to train non-virtual terrain
    
    class terrain( A1FieldCfg.terrain ):
        max_init_terrain_level = 2
        border_size = 5
        slope_treshold = 20.
        curriculum = True

        BarrierTrack_kwargs = merge_dict(A1FieldCfg.terrain.BarrierTrack_kwargs, dict(
            options= [
                "climb",
            ],
            track_block_length= 1.6,
            climb= dict(
                height= (0.2, 0.6), # use this to train in virtual terrain
                # height= (0.1, 0.5), # use this to train in non-virtual terrain
                depth= (0.1, 0.2),
                fake_offset= 0.0, # [m] an offset that make the robot easier to get into the obstacle
                climb_down_prob= 0., # probability of climbing down use it in non-virtual terrain
            ),
            virtual_terrain= False, # Change this to False for real terrain
            no_perlin_threshold= 0.06,
        ))

        TerrainPerlin_kwargs = merge_dict(A1FieldCfg.terrain.TerrainPerlin_kwargs, dict(
            zScale= [0.05, 0.1],
        ))
    
    class commands( A1FieldCfg.commands ):
        class ranges( A1FieldCfg.commands.ranges ):
            lin_vel_x = [0.8, 1.5]
            lin_vel_y = [0.0, 0.0]
            ang_vel_yaw = [0., 0.]

    class termination( A1FieldCfg.termination ):
        # additional factors that determines whether to terminates the episode
        termination_terms = [
            "roll",
            "pitch",
            "z_low",
            "z_high",
            "out_of_track",
        ]
        z_low_kwargs = merge_dict(A1FieldCfg.termination.z_low_kwargs, dict(
            threshold= -1.,
        ))

    class domain_rand( A1FieldCfg.domain_rand ):
        init_base_pos_range = dict(
            x= [0.2, 0.6],
            y= [-0.25, 0.25],
        )

    class rewards( A1FieldCfg.rewards ):
        class scales:
            tracking_ang_vel = 0.1
            world_vel_l2norm = -1.
            legs_energy_substeps = -1e-6
            alive = 2.
            penetrate_depth = -1e-2
            penetrate_volume = -1e-2
            exceed_dof_pos_limits = -1e-1
            exceed_torque_limits_i = -2e-1

    class curriculum( A1FieldCfg.curriculum ):
        penetrate_volume_threshold_harder = 8000
        penetrate_volume_threshold_easier = 12000
        penetrate_depth_threshold_harder = 1000
        penetrate_depth_threshold_easier = 1600


class A1ClimbCfgPPO( A1FieldCfgPPO ):
    class algorithm( A1FieldCfgPPO.algorithm ):
        entropy_coef = 0.0
        clip_min_std = 0.2
    
    class runner( A1FieldCfgPPO.runner ):
        policy_class_name = "ActorCriticRecurrent"
        experiment_name = "field_a1"
        run_name = "".join(["Skill",
        ("Multi" if len(A1ClimbCfg.terrain.BarrierTrack_kwargs["options"]) > 1 else (A1ClimbCfg.terrain.BarrierTrack_kwargs["options"][0] if A1ClimbCfg.terrain.BarrierTrack_kwargs["options"] else "PlaneWalking")),
        ("_pEnergySubsteps{:.0e}".format(A1ClimbCfg.rewards.scales.legs_energy_substeps) if A1ClimbCfg.rewards.scales.legs_energy_substeps != -1e-6 else ""),
        ("_pDofLimit{:.0e}".format(A1ClimbCfg.rewards.scales.exceed_dof_pos_limits) if getattr(A1ClimbCfg.rewards.scales, "exceed_dof_pos_limits") != 0.0 else ""),
        ("_climbDownProb{:.1f}".format(A1ClimbCfg.terrain.BarrierTrack_kwargs["climb"]["climb_down_prob"]) if A1ClimbCfg.terrain.BarrierTrack_kwargs["climb"].get("climb_down_prob", 0.) > 0. else ""),
        ("_climbHeight{:.1f}-{:.1f}".format(*A1ClimbCfg.terrain.BarrierTrack_kwargs["climb"]["height"])),
        ("_propDelay{:.2f}-{:.2f}".format(
                A1ClimbCfg.sensor.proprioception.latency_range[0],
                A1ClimbCfg.sensor.proprioception.latency_range[1],
            ) if A1ClimbCfg.sensor.proprioception.delay_action_obs else ""
        ),
        ("_virtual" if A1ClimbCfg.terrain.BarrierTrack_kwargs["virtual_terrain"] else ""),
        ("_trackBlockLen{:.1f}".format(A1ClimbCfg.terrain.BarrierTrack_kwargs["track_block_length"]) if A1ClimbCfg.terrain.BarrierTrack_kwargs["track_block_length"] != 2. else ""),
        ])
        resume = True
        load_run = "{Your traind walking model directory}"
        load_run = "{Your virtually trained climb model directory}"
        max_iterations = 20000
        save_interval = 500
    