#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include <pybind11/functional.h>
#include "../RocketSim/src/RocketSim.h"
#include "../RocketSim/src/Sim/BallPredTracker/BallPredTracker.h"
#include "../RocketSim/src/Sim/GameEventTracker/GameEventTracker.h"
#include <unordered_map>

namespace py = pybind11;
using namespace RocketSim;

PYBIND11_MODULE(nitro, m) {
    m.doc() = "Python bindings for RocketSim - Rocket League physics simulation";
    m.attr("__version__") = RS_VERSION;

    // ========== Math Types ==========
    
    // Vec - 3D vector
    py::class_<Vec>(m, "Vec")
        .def(py::init<>())
        .def(py::init<float, float, float>(), 
            py::arg("x"), py::arg("y"), py::arg("z"))
        .def_readwrite("x", &Vec::x)
        .def_readwrite("y", &Vec::y)
        .def_readwrite("z", &Vec::z)
        .def("is_zero", &Vec::IsZero)
        .def("to_2d", &Vec::To2D)
        .def("length_sq", &Vec::LengthSq)
        .def("length", &Vec::Length)
        .def("length_sq_2d", &Vec::LengthSq2D)
        .def("length_2d", &Vec::Length2D)
        .def("dot", &Vec::Dot)
        .def("cross", &Vec::Cross)
        .def("dist_sq", &Vec::DistSq)
        .def("dist", &Vec::Dist)
        .def("dist_sq_2d", &Vec::DistSq2D)
        .def("dist_2d", &Vec::Dist2D)
        .def("normalized", &Vec::Normalized)
        .def(py::self + py::self)
        .def(py::self - py::self)
        .def(py::self * py::self)
        .def(py::self / py::self)
        .def(py::self += py::self)
        .def(py::self -= py::self)
        .def(py::self *= py::self)
        .def(py::self /= py::self)
        .def(py::self * float())
        .def(py::self / float())
        .def(py::self *= float())
        .def(py::self /= float())
        .def(float() * py::self)
        .def(float() / py::self)
        .def(py::self < py::self)
        .def(py::self > py::self)
        .def(-py::self)
        .def(py::self == py::self)
        .def(py::self != py::self)
        .def("__getitem__", [](const Vec &v, uint32_t i) { return v[i]; })
        .def("__setitem__", [](Vec &v, uint32_t i, float val) { v[i] = val; })
        .def("__repr__", [](const Vec &v) {
            return "Vec(" + std::to_string(v.x) + ", " + std::to_string(v.y) + ", " + std::to_string(v.z) + ")";
        });

    // RotMat - 3x3 rotation matrix
    py::class_<RotMat>(m, "RotMat")
        .def(py::init<>())
        .def(py::init<Vec, Vec, Vec>(),
            py::arg("forward"), py::arg("right"), py::arg("up"))
        .def_readwrite("forward", &RotMat::forward)
        .def_readwrite("right", &RotMat::right)
        .def_readwrite("up", &RotMat::up)
        .def_static("get_identity", &RotMat::GetIdentity)
        .def_static("look_at", &RotMat::LookAt,
            py::arg("forward_dir"), py::arg("up_dir"))
        .def("dot", py::overload_cast<const Vec&>(&RotMat::Dot, py::const_))
        .def("dot", py::overload_cast<const RotMat&>(&RotMat::Dot, py::const_))
        .def("transpose", &RotMat::Transpose)
        .def(py::self + py::self)
        .def(py::self - py::self)
        .def(py::self += py::self)
        .def(py::self -= py::self)
        .def(py::self * float())
        .def(py::self / float())
        .def(py::self *= float())
        .def(py::self /= float())
        .def(py::self == py::self)
        .def(py::self != py::self)
        .def("__repr__", [](const RotMat &r) {
            return "RotMat(forward=" + std::to_string(r.forward.x) + "," + std::to_string(r.forward.y) + "," + std::to_string(r.forward.z) + ")";
        });

    // Angle - Euler angles in radians
    py::class_<Angle>(m, "Angle")
        .def(py::init<float, float, float>(),
            py::arg("yaw") = 0, py::arg("pitch") = 0, py::arg("roll") = 0)
        .def_readwrite("yaw", &Angle::yaw)
        .def_readwrite("pitch", &Angle::pitch)
        .def_readwrite("roll", &Angle::roll)
        .def_static("from_rot_mat", &Angle::FromRotMat)
        .def("to_rot_mat", &Angle::ToRotMat)
        .def_static("from_vec", &Angle::FromVec)
        .def("get_forward_vec", &Angle::GetForwardVec)
        .def("normalize_fix", &Angle::NormalizeFix)
        .def("get_delta_to", &Angle::GetDeltaTo)
        .def(py::self + py::self)
        .def(py::self - py::self)
        .def(py::self == py::self)
        .def("__getitem__", [](const Angle &a, size_t i) { return a[i]; })
        .def("__setitem__", [](Angle &a, size_t i, float val) { a[i] = val; })
        .def("__repr__", [](const Angle &a) {
            return "Angle(yaw=" + std::to_string(a.yaw) + ", pitch=" + std::to_string(a.pitch) + ", roll=" + std::to_string(a.roll) + ")";
        });

    // ========== Game Types ==========

    // GameMode enum
    py::enum_<GameMode>(m, "GameMode")
        .value("SOCCAR", GameMode::SOCCAR)
        .value("HOOPS", GameMode::HOOPS)
        .value("HEATSEEKER", GameMode::HEATSEEKER)
        .value("SNOWDAY", GameMode::SNOWDAY)
        .value("DROPSHOT", GameMode::DROPSHOT)
        .value("THE_VOID", GameMode::THE_VOID)
        .export_values();

    // Team enum
    py::enum_<Team>(m, "Team")
        .value("BLUE", Team::BLUE)
        .value("ORANGE", Team::ORANGE)
        .export_values();

    // ========== Physics State ==========

    py::class_<PhysState>(m, "PhysState")
        .def(py::init<>())
        .def_readwrite("pos", &PhysState::pos)
        .def_readwrite("rot_mat", &PhysState::rotMat)
        .def_readwrite("vel", &PhysState::vel)
        .def_readwrite("ang_vel", &PhysState::angVel)
        .def("get_inverted_y", &PhysState::GetInvertedY);

    // ========== Car ==========

    // CarControls
    py::class_<CarControls>(m, "CarControls")
        .def(py::init<>())
        .def_readwrite("throttle", &CarControls::throttle)
        .def_readwrite("steer", &CarControls::steer)
        .def_readwrite("pitch", &CarControls::pitch)
        .def_readwrite("yaw", &CarControls::yaw)
        .def_readwrite("roll", &CarControls::roll)
        .def_readwrite("jump", &CarControls::jump)
        .def_readwrite("boost", &CarControls::boost)
        .def_readwrite("handbrake", &CarControls::handbrake)
        .def("clamp_fix", &CarControls::ClampFix);

    // BallHitInfo
    py::class_<BallHitInfo>(m, "BallHitInfo")
        .def(py::init<>())
        .def_readwrite("is_valid", &BallHitInfo::isValid)
        .def_readwrite("relative_pos_on_ball", &BallHitInfo::relativePosOnBall)
        .def_readwrite("ball_pos", &BallHitInfo::ballPos)
        .def_readwrite("extra_hit_vel", &BallHitInfo::extraHitVel)
        .def_readwrite("tick_count_when_hit", &BallHitInfo::tickCountWhenHit)
        .def_readwrite("tick_count_when_extra_impulse_applied", &BallHitInfo::tickCountWhenExtraImpulseApplied);

    // CarState
    py::class_<CarState, PhysState>(m, "CarState")
        .def(py::init<>())
        .def_readwrite("is_on_ground", &CarState::isOnGround)
        .def_property("wheels_with_contact",
            [](const CarState &s) { return std::vector<bool>(s.wheelsWithContact, s.wheelsWithContact + 4); },
            [](CarState &s, const std::vector<bool> &v) { 
                for (size_t i = 0; i < 4 && i < v.size(); ++i) s.wheelsWithContact[i] = v[i]; 
            })
        .def_readwrite("has_jumped", &CarState::hasJumped)
        .def_readwrite("has_double_jumped", &CarState::hasDoubleJumped)
        .def_readwrite("has_flipped", &CarState::hasFlipped)
        .def_readwrite("flip_rel_torque", &CarState::flipRelTorque)
        .def_readwrite("jump_time", &CarState::jumpTime)
        .def_readwrite("flip_time", &CarState::flipTime)
        .def_readwrite("is_flipping", &CarState::isFlipping)
        .def_readwrite("is_jumping", &CarState::isJumping)
        .def_readwrite("air_time", &CarState::airTime)
        .def_readwrite("air_time_since_jump", &CarState::airTimeSinceJump)
        .def_readwrite("boost", &CarState::boost)
        .def_readwrite("time_since_boosted", &CarState::timeSinceBoosted)
        .def_readwrite("is_boosting", &CarState::isBoosting)
        .def_readwrite("boosting_time", &CarState::boostingTime)
        .def_readwrite("is_supersonic", &CarState::isSupersonic)
        .def_readwrite("supersonic_time", &CarState::supersonicTime)
        .def_readwrite("handbrake_val", &CarState::handbrakeVal)
        .def_readwrite("is_auto_flipping", &CarState::isAutoFlipping)
        .def_readwrite("auto_flip_timer", &CarState::autoFlipTimer)
        .def_readwrite("auto_flip_torque_scale", &CarState::autoFlipTorqueScale)
        .def_readwrite("is_demoed", &CarState::isDemoed)
        .def_readwrite("demo_respawn_timer", &CarState::demoRespawnTimer)
        .def_readwrite("ball_hit_info", &CarState::ballHitInfo)
        .def_readwrite("last_controls", &CarState::lastControls)
        .def("has_flip_or_jump", &CarState::HasFlipOrJump)
        .def("has_flip_reset", &CarState::HasFlipReset)
        .def("got_flip_reset", &CarState::GotFlipReset);

    // WheelPairConfig
    py::class_<WheelPairConfig>(m, "WheelPairConfig")
        .def(py::init<>())
        .def_readwrite("wheel_radius", &WheelPairConfig::wheelRadius)
        .def_readwrite("suspension_rest_length", &WheelPairConfig::suspensionRestLength)
        .def_readwrite("connection_point_offset", &WheelPairConfig::connectionPointOffset);

    // CarConfig
    py::class_<CarConfig>(m, "CarConfig")
        .def(py::init<>())
        .def_readwrite("hitbox_size", &CarConfig::hitboxSize)
        .def_readwrite("hitbox_pos_offset", &CarConfig::hitboxPosOffset)
        .def_readwrite("front_wheels", &CarConfig::frontWheels)
        .def_readwrite("back_wheels", &CarConfig::backWheels)
        .def_readwrite("three_wheels", &CarConfig::threeWheels)
        .def_readwrite("dodge_deadzone", &CarConfig::dodgeDeadzone);

    // Preset car configs
    m.attr("CAR_CONFIG_OCTANE") = CAR_CONFIG_OCTANE;
    m.attr("CAR_CONFIG_DOMINUS") = CAR_CONFIG_DOMINUS;
    m.attr("CAR_CONFIG_PLANK") = CAR_CONFIG_PLANK;
    m.attr("CAR_CONFIG_BREAKOUT") = CAR_CONFIG_BREAKOUT;
    m.attr("CAR_CONFIG_HYBRID") = CAR_CONFIG_HYBRID;
    m.attr("CAR_CONFIG_MERC") = CAR_CONFIG_MERC;

    // Car class
    py::class_<Car>(m, "Car")
        .def_readwrite("config", &Car::config)
        .def_readwrite("team", &Car::team)
        .def_readonly("id", &Car::id)
        .def_readwrite("controls", &Car::controls)
        .def_property("state", 
            [](Car &c) { return c.GetState(); },
            [](Car &c, const CarState &s) { c.SetState(s); })
        .def("get_state", &Car::GetState)
        .def("set_state", &Car::SetState)
        .def("respawn", &Car::Respawn,
            py::arg("game_mode"), py::arg("seed") = -1, py::arg("boost_amount") = 33.f)
        .def("demolish", &Car::Demolish)
        .def("get_forward_dir", &Car::GetForwardDir)
        .def("get_right_dir", &Car::GetRightDir)
        .def("get_up_dir", &Car::GetUpDir);

    // ========== Ball ==========

    // BallState
    py::class_<BallState, PhysState>(m, "BallState")
        .def(py::init<>());

    // Ball class
    py::class_<Ball>(m, "Ball")
        .def_property("state",
            [](Ball &b) { return b.GetState(); },
            [](Ball &b, const BallState &s) { b.SetState(s); })
        .def("get_state", &Ball::GetState)
        .def("set_state", &Ball::SetState);

    // ========== Boost Pads ==========

    // BoostPadConfig
    py::class_<BoostPadConfig>(m, "BoostPadConfig")
        .def(py::init<>())
        .def_readwrite("pos", &BoostPadConfig::pos)
        .def_readwrite("is_big", &BoostPadConfig::isBig);

    // BoostPadState
    py::class_<BoostPadState>(m, "BoostPadState")
        .def(py::init<>())
        .def_readwrite("is_active", &BoostPadState::isActive)
        .def_readwrite("cooldown", &BoostPadState::cooldown);

    // BoostPad
    py::class_<BoostPad>(m, "BoostPad")
        .def_readwrite("config", &BoostPad::config)
        .def("get_state", &BoostPad::GetState)
        .def("set_state", &BoostPad::SetState);

    // ========== Arena Configuration ==========

    // DemoMode enum
    py::enum_<DemoMode>(m, "DemoMode")
        .value("NORMAL", DemoMode::NORMAL)
        .value("ON_CONTACT", DemoMode::ON_CONTACT)
        .value("DISABLED", DemoMode::DISABLED)
        .export_values();

    // MutatorConfig
    py::class_<MutatorConfig>(m, "MutatorConfig")
        .def(py::init<GameMode>(), py::arg("game_mode"))
        .def_readwrite("car_mass", &MutatorConfig::carMass)
        .def_readwrite("car_world_friction", &MutatorConfig::carWorldFriction)
        .def_readwrite("car_world_restitution", &MutatorConfig::carWorldRestitution)
        .def_readwrite("ball_mass", &MutatorConfig::ballMass)
        .def_readwrite("ball_max_speed", &MutatorConfig::ballMaxSpeed)
        .def_readwrite("ball_drag", &MutatorConfig::ballDrag)
        .def_readwrite("ball_world_friction", &MutatorConfig::ballWorldFriction)
        .def_readwrite("ball_world_restitution", &MutatorConfig::ballWorldRestitution)
        .def_readwrite("jump_accel", &MutatorConfig::jumpAccel)
        .def_readwrite("jump_immediate_force", &MutatorConfig::jumpImmediateForce)
        .def_readwrite("boost_accel_ground", &MutatorConfig::boostAccelGround)
        .def_readwrite("boost_accel_air", &MutatorConfig::boostAccelAir)
        .def_readwrite("boost_used_per_second", &MutatorConfig::boostUsedPerSecond)
        .def_readwrite("respawn_delay", &MutatorConfig::respawnDelay)
        .def_readwrite("bump_cooldown_time", &MutatorConfig::bumpCooldownTime)
        .def_readwrite("boost_pad_cooldown_big", &MutatorConfig::boostPadCooldown_Big)
        .def_readwrite("boost_pad_cooldown_small", &MutatorConfig::boostPadCooldown_Small)
        .def_readwrite("car_spawn_boost_amount", &MutatorConfig::carSpawnBoostAmount)
        .def_readwrite("ball_hit_extra_force_scale", &MutatorConfig::ballHitExtraForceScale)
        .def_readwrite("bump_force_scale", &MutatorConfig::bumpForceScale)
        .def_readwrite("ball_radius", &MutatorConfig::ballRadius)
        .def_readwrite("unlimited_flips", &MutatorConfig::unlimitedFlips)
        .def_readwrite("unlimited_double_jumps", &MutatorConfig::unlimitedDoubleJumps)
        .def_readwrite("demo_mode", &MutatorConfig::demoMode)
        .def_readwrite("enable_team_demos", &MutatorConfig::enableTeamDemos);

    // ArenaMemWeightMode enum
    py::enum_<ArenaMemWeightMode>(m, "ArenaMemWeightMode")
        .value("HEAVY", ArenaMemWeightMode::HEAVY)
        .value("LIGHT", ArenaMemWeightMode::LIGHT)
        .export_values();

    // ArenaConfig
    py::class_<ArenaConfig>(m, "ArenaConfig")
        .def(py::init<>())
        .def_readwrite("mem_weight_mode", &ArenaConfig::memWeightMode)
        .def_readwrite("min_pos", &ArenaConfig::minPos)
        .def_readwrite("max_pos", &ArenaConfig::maxPos)
        .def_readwrite("max_aabb_len", &ArenaConfig::maxAABBLen)
        .def_readwrite("no_ball_rot", &ArenaConfig::noBallRot)
        .def_readwrite("use_custom_broadphase", &ArenaConfig::useCustomBroadphase)
        .def_readwrite("max_objects", &ArenaConfig::maxObjects);

    // ========== Arena ==========

    py::class_<Arena>(m, "Arena")
        .def_readonly("game_mode", &Arena::gameMode)
        .def_readonly("tick_count", &Arena::tickCount)
        .def_property("tick_rate",
            [](Arena &a) { return a.GetTickRate(); },
            [](Arena &a, float rate) { a.tickTime = 1.0f / rate; })
        .def_readwrite("tick_time", &Arena::tickTime)
        .def_readonly("ball", &Arena::ball)
        .def_static("create", &Arena::Create,
            py::arg("game_mode"),
            py::arg("arena_config") = ArenaConfig(),
            py::arg("tick_rate") = 120.0f,
            py::return_value_policy::take_ownership)
        .def("get_cars", [](Arena &a) {
            std::vector<Car*> cars(a.GetCars().begin(), a.GetCars().end());
            return cars;
        })
        .def("add_car", &Arena::AddCar,
            py::arg("team"),
            py::arg("config") = CAR_CONFIG_OCTANE,
            py::return_value_policy::reference_internal)
        .def("remove_car", py::overload_cast<uint32_t>(&Arena::RemoveCar))
        .def("get_car", &Arena::GetCar,
            py::arg("id"),
            py::return_value_policy::reference_internal)
        .def("step", &Arena::Step, py::arg("ticks_to_simulate") = 1)
        .def("reset_to_random_kickoff", &Arena::ResetToRandomKickoff,
            py::arg("seed") = -1)
        .def("is_ball_probably_going_in", &Arena::IsBallProbablyGoingIn,
            py::arg("max_time") = 2.0f,
            py::arg("extra_margin") = 0.0f,
            py::arg("goal_team_out") = nullptr)
        .def("is_ball_scored", &Arena::IsBallScored)
        .def("get_mutator_config", &Arena::GetMutatorConfig)
        .def("set_mutator_config", &Arena::SetMutatorConfig)
        .def("get_arena_config", &Arena::GetArenaConfig)
        .def("get_boost_pads", [](Arena &a) {
            const auto& pads = a.GetBoostPads();
            std::vector<BoostPad*> result(pads.begin(), pads.end());
            return result;
        }, py::return_value_policy::reference_internal)
        .def("clone", &Arena::Clone,
            py::arg("copy_callbacks") = false,
            py::return_value_policy::take_ownership)
        .def("set_goal_score_callback", [](Arena &a, py::function callback) {
            // Store callback in a static map to keep it alive
            static std::unordered_map<Arena*, py::function> callbacks;
            callbacks[&a] = callback;
            
            a.SetGoalScoreCallback([](Arena* arena, Team scoringTeam, void* userInfo) {
                auto it = callbacks.find(arena);
                if (it != callbacks.end()) {
                    py::gil_scoped_acquire acquire;
                    try {
                        it->second(arena, scoringTeam);
                    } catch (const py::error_already_set& e) {
                        py::print("Error in goal score callback:", e.what());
                    }
                }
            }, nullptr);
        }, py::arg("callback"))
        .def("set_car_bump_callback", [](Arena &a, py::function callback) {
            // Store callback in a static map to keep it alive
            static std::unordered_map<Arena*, py::function> callbacks;
            callbacks[&a] = callback;
            
            a.SetCarBumpCallback([](Arena* arena, Car* bumper, Car* bumped, bool isDemo, void* userInfo) {
                auto it = callbacks.find(arena);
                if (it != callbacks.end()) {
                    py::gil_scoped_acquire acquire;
                    try {
                        it->second(arena, bumper, bumped, isDemo);
                    } catch (const py::error_already_set& e) {
                        py::print("Error in car bump callback:", e.what());
                    }
                }
            }, nullptr);
        }, py::arg("callback"));

    // ========== Ball Prediction ==========

    py::class_<BallPredTracker>(m, "BallPredTracker")
        .def(py::init<Arena*, size_t>(),
            py::arg("arena"), py::arg("num_pred_ticks"))
        .def_readonly("pred_data", &BallPredTracker::predData)
        .def_readonly("num_pred_ticks", &BallPredTracker::numPredTicks)
        .def("update_from_arena", &BallPredTracker::UpdatePredFromArena,
            py::arg("arena"))
        .def("update_manual", &BallPredTracker::UpdatePredManual,
            py::arg("cur_ball_state"), py::arg("ticks_since_last_update"))
        .def("force_update_all", &BallPredTracker::ForceUpdateAllPred,
            py::arg("initial_ball_state"))
        .def("get_ball_state_for_time", &BallPredTracker::GetBallStateForTime,
            py::arg("pred_time"));

    // ========== Game Event Tracking ==========

    py::class_<GameEventTrackerConfig>(m, "GameEventTrackerConfig")
        .def(py::init<>())
        .def_readwrite("shot_min_speed", &GameEventTrackerConfig::shotMinSpeed)
        .def_readwrite("shot_touch_min_delay", &GameEventTrackerConfig::shotTouchMinDelay)
        .def_readwrite("pred_score_extra_margin", &GameEventTrackerConfig::predScoreExtraMargin)
        .def_readwrite("shot_event_cooldown", &GameEventTrackerConfig::shotEventCooldown)
        .def_readwrite("shot_min_score_time", &GameEventTrackerConfig::shotMinScoreTime)
        .def_readwrite("goal_max_touch_time", &GameEventTrackerConfig::goalMaxTouchTime)
        .def_readwrite("pass_max_touch_time", &GameEventTrackerConfig::passMaxTouchTime);

    py::class_<GameEventTracker>(m, "GameEventTracker")
        .def(py::init<>())
        .def_readwrite("config", &GameEventTracker::config)
        .def_readwrite("auto_state_set_detection", &GameEventTracker::autoStateSetDetection)
        .def("update", &GameEventTracker::Update, py::arg("arena"))
        .def("reset_persistent_info", &GameEventTracker::ResetPersistentInfo)
        .def("set_shot_callback", [](GameEventTracker &t, py::function callback) {
            static std::unordered_map<GameEventTracker*, py::function> callbacks;
            callbacks[&t] = callback;
            
            t.SetShotCallback([](Arena* arena, Car* shooter, Car* passer, void* userInfo) {
                auto it = callbacks.find(static_cast<GameEventTracker*>(userInfo));
                if (it != callbacks.end()) {
                    py::gil_scoped_acquire acquire;
                    try {
                        it->second(arena, shooter, passer);
                    } catch (const py::error_already_set& e) {
                        py::print("Error in shot callback:", e.what());
                    }
                }
            }, &t);
        }, py::arg("callback"))
        .def("set_goal_callback", [](GameEventTracker &t, py::function callback) {
            static std::unordered_map<GameEventTracker*, py::function> callbacks;
            callbacks[&t] = callback;
            
            t.SetGoalCallback([](Arena* arena, Car* scorer, Car* passer, void* userInfo) {
                auto it = callbacks.find(static_cast<GameEventTracker*>(userInfo));
                if (it != callbacks.end()) {
                    py::gil_scoped_acquire acquire;
                    try {
                        it->second(arena, scorer, passer);
                    } catch (const py::error_already_set& e) {
                        py::print("Error in goal callback:", e.what());
                    }
                }
            }, &t);
        }, py::arg("callback"))
        .def("set_save_callback", [](GameEventTracker &t, py::function callback) {
            static std::unordered_map<GameEventTracker*, py::function> callbacks;
            callbacks[&t] = callback;
            
            t.SetSaveCallback([](Arena* arena, Car* saver, void* userInfo) {
                auto it = callbacks.find(static_cast<GameEventTracker*>(userInfo));
                if (it != callbacks.end()) {
                    py::gil_scoped_acquire acquire;
                    try {
                        it->second(arena, saver);
                    } catch (const py::error_already_set& e) {
                        py::print("Error in save callback:", e.what());
                    }
                }
            }, &t);
        }, py::arg("callback"));

    // ========== Initialization ==========

    m.def("init", 
        [](const std::string& collision_meshes_folder, bool silent = false) {
            Init(std::filesystem::path(collision_meshes_folder), silent);
        },
        py::arg("collision_meshes_folder"),
        py::arg("silent") = false,
        "Initialize RocketSim with collision mesh folder");

    m.def("get_stage", &GetStage, "Get the current initialization stage");

    // RocketSimStage enum
    py::enum_<RocketSimStage>(m, "RocketSimStage")
        .value("UNINITIALIZED", RocketSimStage::UNINITIALIZED)
        .value("INITIALIZING", RocketSimStage::INITIALIZING)
        .value("INITIALIZED", RocketSimStage::INITIALIZED)
        .export_values();
}
