"""Advanced example using ball prediction, event tracking, and callbacks"""

import nitro as rs


def main():
    # Initialize RocketSim
    rs.init("collision_meshes")

    # Create arena
    arena = rs.Arena.create(rs.GameMode.SOCCAR, tick_rate=120.0)

    # Add cars for both teams
    blue_car = arena.add_car(rs.Team.BLUE, rs.CAR_CONFIG_OCTANE)
    orange_car = arena.add_car(rs.Team.ORANGE, rs.CAR_CONFIG_OCTANE)

    print("=== Advanced RocketSim Demo ===\n")

    # === Ball Prediction ===
    print("1. Ball Prediction")
    print("-" * 40)

    # Create ball prediction tracker (6 seconds = 720 ticks)
    pred_tracker = rs.BallPredTracker(arena, 720)

    # Show ball predictions
    print("Initial ball prediction:")
    for t in [0.5, 1.0, 2.0, 3.0]:
        pred_state = pred_tracker.get_ball_state_for_time(t)
        print(f"  t={t:.1f}s: pos={pred_state.pos}, vel={pred_state.vel.length():.0f}")

    print()

    # === Event Tracking ===
    print("2. Game Event Tracking")
    print("-" * 40)

    event_tracker = rs.GameEventTracker()

    # Configure event detection
    event_tracker.config.shot_min_speed = 1500.0  # Lower threshold for demo

    # Track events
    events = {"shots": [], "goals": [], "saves": []}

    def on_shot(arena, shooter, passer):
        shooter_team = "Blue" if shooter.team == rs.Team.BLUE else "Orange"
        msg = f"SHOT by {shooter_team} car {shooter.id}"
        if passer:
            passer_team = "Blue" if passer.team == rs.Team.BLUE else "Orange"
            msg += f" (assist from {passer_team} car {passer.id})"
        print(f"  🎯 {msg}")
        events["shots"].append(shooter.id)

    def on_goal(arena, scorer, passer):
        scorer_team = "Blue" if scorer.team == rs.Team.BLUE else "Orange"
        msg = f"GOAL by {scorer_team} car {scorer.id}"
        if passer:
            passer_team = "Blue" if passer.team == rs.Team.BLUE else "Orange"
            msg += f" (assist from {passer_team} car {passer.id})"
        print(f"  ⚽ {msg}")
        events["goals"].append(scorer.id)

    def on_save(arena, saver):
        saver_team = "Blue" if saver.team == rs.Team.BLUE else "Orange"
        print(f"  🛡️  SAVE by {saver_team} car {saver.id}")
        events["saves"].append(saver.id)

    event_tracker.set_shot_callback(on_shot)
    event_tracker.set_goal_callback(on_goal)
    event_tracker.set_save_callback(on_save)

    # === Arena Callbacks ===
    print("\n3. Arena Event Callbacks")
    print("-" * 40)

    arena_events = {"goals": [], "bumps": [], "demos": []}

    def on_arena_goal(arena, scoring_team):
        team_name = "Blue" if scoring_team == rs.Team.BLUE else "Orange"
        print(f"  📢 ARENA: {team_name} team scored!")
        arena_events["goals"].append(scoring_team)

    def on_car_bump(arena, bumper, bumped, is_demo):
        if is_demo:
            print(f"  💥 DEMO: Car {bumper.id} demolished car {bumped.id}!")
            arena_events["demos"].append((bumper.id, bumped.id))
        else:
            print(f"  🏃 BUMP: Car {bumper.id} bumped car {bumped.id}")
            arena_events["bumps"].append((bumper.id, bumped.id))

    arena.set_goal_score_callback(on_arena_goal)
    arena.set_car_bump_callback(on_car_bump)

    # === Simulation ===
    print("\n4. Running Simulation")
    print("-" * 40)

    # Reset to kickoff
    arena.reset_to_random_kickoff(seed=42)

    # Simulate 5 seconds of gameplay
    print("Simulating 5 seconds...")
    for tick in range(600):
        # Simple AI: drive toward ball
        ball_pos = arena.ball.get_state().pos

        for car in [blue_car, orange_car]:
            car_pos = car.get_state().pos
            distance = ball_pos.dist(car_pos)

            if distance > 200:
                car.controls.throttle = 1.0
                car.controls.boost = distance > 1500
            else:
                car.controls.throttle = 0.5

        # Step simulation
        arena.step(1)

        # Update event tracker
        event_tracker.update(arena)

        # Update ball prediction every 30 ticks (0.25s)
        if tick % 30 == 0:
            pred_tracker.update_from_arena(arena)

    # === Results ===
    print("\n5. Simulation Results")
    print("-" * 40)
    print(f"Total ticks: {arena.tick_count}")
    print(f"Shots detected: {len(events['shots'])}")
    print(f"Goals detected: {len(events['goals'])}")
    print(f"Saves detected: {len(events['saves'])}")
    print(f"Bumps: {len(arena_events['bumps'])}")
    print(f"Demos: {len(arena_events['demos'])}")

    # Show final ball prediction
    print("\n6. Final Ball Prediction")
    print("-" * 40)
    final_pred = pred_tracker.get_ball_state_for_time(1.0)
    print(f"Ball in 1 second: pos={final_pred.pos}")
    print(f"                  vel={final_pred.vel.length():.0f} uu/s")

    # Get boost pad states
    print("\n7. Boost Pad States")
    print("-" * 40)
    pads = arena.get_boost_pads()
    active_pads = [p for p in pads if p.get_state().is_active]
    inactive_pads = [p for p in pads if not p.get_state().is_active]
    print(f"Active pads: {len(active_pads)}/{len(pads)}")
    print(f"Pads on cooldown: {len(inactive_pads)}")

    print("\n✅ Demo complete!")


if __name__ == "__main__":
    main()
