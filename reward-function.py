import math

def reward_function(params):
    """
    針對 Forever Raceway 優化的獎勵函數
    
    Forever Raceway 特徵：
    - 短直道 + 急彎（90度轉彎）
    - 逆時針方向
    - 需要精準的速度控制和轉向
    
    策略：
    1. 在直道上獎勵高速
    2. 在彎道前減速，彎道中適度速度
    3. 獎勵平滑的轉向
    4. 懲罰出軌和不穩定行為
    """
    
    # ============ 讀取參數 ============
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    speed = params['speed']
    steering_angle = params['steering_angle']
    steering_abs = abs(steering_angle)
    all_wheels_on_track = params['all_wheels_on_track']
    progress = params['progress']
    steps = params['steps']
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    heading = params['heading']
    is_offtrack = params['is_offtrack']
    
    # 基礎獎勵
    reward = 1.0
    
    # ============ 1. 出軌懲罰 ============
    if not all_wheels_on_track or is_offtrack:
        return 1e-3
    
    # ============ 2. 計算當前位置的賽道曲率 ============
    # 使用前方的 waypoints 來預測彎道
    next_point = waypoints[closest_waypoints[1]]
    
    # 往前看更多點來判斷是否接近彎道
    look_ahead = 5  # 往前看 5 個 waypoints
    future_index = (closest_waypoints[1] + look_ahead) % len(waypoints)
    future_point = waypoints[future_index]
    
    # 計算方向變化（用來判斷彎道）
    current_index = closest_waypoints[0]
    prev_index = (current_index - 1) % len(waypoints)
    next_index = closest_waypoints[1]
    
    prev_point = waypoints[prev_index]
    curr_point = waypoints[current_index]
    next_point_2 = waypoints[next_index]
    
    # 計算兩段路徑的方向
    heading_current = math.atan2(
        curr_point[1] - prev_point[1],
        curr_point[0] - prev_point[0]
    )
    heading_next = math.atan2(
        next_point_2[1] - curr_point[1],
        next_point_2[0] - curr_point[0]
    )
    
    # 計算曲率（方向變化）
    direction_diff = abs(heading_next - heading_current)
    if direction_diff > math.pi:
        direction_diff = 2 * math.pi - direction_diff
    
    # 轉換為角度
    direction_diff_deg = math.degrees(direction_diff)
    
    # 判斷是直道還是彎道
    is_straight = direction_diff_deg < 5
    is_mild_turn = 5 <= direction_diff_deg < 15
    is_sharp_turn = direction_diff_deg >= 15
    
    # ============ 3. 速度獎勵策略 ============
    # 速度範圍：0.5 ~ 3.0 m/s
    MAX_SPEED = 3.0
    MIN_SPEED = 0.5
    
    if is_straight:
        # 直道：獎勵高速
        optimal_speed = MAX_SPEED
        if speed >= 2.5:
            speed_reward = 1.0
        elif speed >= 2.0:
            speed_reward = 0.8
        else:
            speed_reward = 0.5
    elif is_mild_turn:
        # 緩彎：中等速度
        optimal_speed = 2.0
        if 1.5 <= speed <= 2.5:
            speed_reward = 1.0
        elif speed > 2.5:
            speed_reward = 0.6  # 太快要減分
        else:
            speed_reward = 0.7
    else:  # is_sharp_turn
        # 急彎：控制速度
        optimal_speed = 1.5
        if 1.0 <= speed <= 2.0:
            speed_reward = 1.0
        elif speed > 2.5:
            speed_reward = 0.4  # 急彎太快很危險
        else:
            speed_reward = 0.7
    
    reward *= speed_reward
    
    # ============ 4. 中心線獎勵（根據彎道調整） ============
    # 直道上貼近中心，彎道允許較寬的範圍
    
    if is_straight:
        # 直道：嚴格要求靠近中心
        marker_1 = 0.1 * track_width
        marker_2 = 0.2 * track_width
        marker_3 = 0.4 * track_width
    else:
        # 彎道：允許較寬的行駛範圍（racing line）
        marker_1 = 0.15 * track_width
        marker_2 = 0.3 * track_width
        marker_3 = 0.5 * track_width
    
    if distance_from_center <= marker_1:
        center_reward = 1.0
    elif distance_from_center <= marker_2:
        center_reward = 0.7
    elif distance_from_center <= marker_3:
        center_reward = 0.3
    else:
        center_reward = 0.1
    
    reward *= center_reward
    
    # ============ 5. 轉向平滑度獎勵 ============
    # 懲罰過度轉向，鼓勵平滑駕駛
    
    STEERING_THRESHOLD = 20  # 度
    
    if steering_abs < 10:
        steering_reward = 1.0
    elif steering_abs < 20:
        steering_reward = 0.8
    elif steering_abs < 25:
        steering_reward = 0.6
    else:
        steering_reward = 0.4  # 極端轉向
    
    # 但在急彎時，適當轉向是必要的
    if is_sharp_turn and steering_abs > 15:
        steering_reward = max(steering_reward, 0.7)
    
    reward *= steering_reward
    
    # ============ 6. 速度-轉向協調獎勵 ============
    # 高速時不應該有大角度轉向
    
    if speed > 2.5 and steering_abs > 20:
        # 高速急轉是危險的
        reward *= 0.5
    elif speed > 2.0 and steering_abs > 25:
        reward *= 0.6
    
    # ============ 7. 進度效率獎勵 ============
    # 鼓勵高效完成賽道
    
    if steps > 0:
        progress_reward = (progress / steps) * 5.0
        reward += progress_reward
    
    # ============ 8. 完成圈獎勵 ============
    if progress == 100:
        reward += 100.0
    
    # ============ 9. 方向對齊獎勵 ============
    # 確保車頭朝向正確方向
    
    # 計算理想方向
    track_direction = math.atan2(
        next_point_2[1] - curr_point[1],
        next_point_2[0] - curr_point[0]
    )
    track_direction_deg = math.degrees(track_direction)
    
    # 計算方向差異
    direction_error = abs(track_direction_deg - heading)
    if direction_error > 180:
        direction_error = 360 - direction_error
    
    if direction_error < 10:
        heading_reward = 1.0
    elif direction_error < 20:
        heading_reward = 0.8
    elif direction_error < 30:
        heading_reward = 0.6
    else:
        heading_reward = 0.4
    
    reward *= heading_reward
    
    return float(reward)
