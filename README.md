# nsysu-mis-dl-deepracer
2025 NSYSU Winter Semster Final Project Challenge : AWS Deep acer
# AWS DeepRacer - Forever Raceway 優化專案

![DeepRacer](https://img.shields.io/badge/AWS-DeepRacer-orange)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![SAC](https://img.shields.io/badge/Algorithm-SAC-green)

針對 AWS DeepRacer Forever Raceway 賽道優化的強化學習專案，採用 Soft Actor-Critic (SAC) 演算法，透過精心設計的獎勵函數實現高效的自動駕駛策略。

## 📊 性能表現

- **最佳圈速**: 11 秒
- **訓練前基準**: 13+ 秒
- **改善幅度**: ~18% 圈速提升

## 🏁 賽道特徵

**Forever Raceway** 是一個技術型賽道，具有以下特點：

- **方向**: 逆時針 (Counterclockwise)
- **賽道類型**: 短直道 + 急彎組合
- **轉彎角度**: 多處 90 度急轉彎
- **難度重點**: 
  - 速度控制的精準性
  - 直道與彎道的速度切換
  - 轉向角度的優化

## 🎯 獎勵函數策略

本專案的獎勵函數採用多維度評估策略，針對 Forever Raceway 的特性進行優化：

### 1. 動態速度策略
根據賽道曲率自適應調整速度獎勵：

| 賽道類型 | 最佳速度 | 策略 |
|---------|---------|------|
| **直道** (`< 5°`) | 2.5 - 3.0 m/s | 高速行駛，最大化直道效率 |
| **緩彎** (`5° - 15°`) | 1.5 - 2.5 m/s | 中等速度，保持穩定性 |
| **急彎** (`≥ 15°`) | 1.0 - 2.0 m/s | 控制速度，避免出軌 |

### 2. 賽道中心線優化
- **直道**: 嚴格要求靠近中心線 (0.1 - 0.4 track width)
- **彎道**: 允許較寬的 racing line (0.15 - 0.5 track width)

### 3. 轉向平滑度
- 鼓勵平滑轉向 (`< 10°`)
- 懲罰過度轉向 (`> 25°`)
- 急彎時允許較大轉向角度

### 4. 速度-轉向協調
- 高速 (`> 2.5 m/s`) + 大角度轉向 (`> 20°`) → 懲罰 50%
- 防止危險的高速急轉操作

### 5. 方向對齊
- 計算車頭方向與賽道方向的偏差
- 獎勵方向偏差 `< 10°` 的行駛狀態

### 6. 進度效率
- 鼓勵高效完成賽道: `(progress / steps) × 5.0`
- 完成圈獎勵: `+100.0`

## ⚙️ 訓練配置

### 基本設定
```yaml
Race Type: Time trial
Environment: Forever Raceway - Counterclockwise
Sensor: Camera
Framework: TensorFlow
```

### Action Space
```yaml
Type: Continuous
Speed Range: [0.5, 3.5] m/s
Steering Angle: [-30, 30]°
```

### 強化學習演算法
```yaml
Algorithm: SAC (Soft Actor-Critic)
```

### 超參數配置

| 超參數 | 數值 | 說明 |
|-------|------|------|
| **Gradient descent batch size** | 64 | 梯度下降批次大小 |
| **Discount factor (γ)** | 0.999 | 折扣因子，重視長期獎勵 |
| **Loss type** | Mean squared error | 損失函數類型 |
| **Learning rate** | 0.0003 | 學習率 |
| **Experience episodes** | 1 | 每次策略更新間的經驗回合數 |
| **SAC alpha (α)** | 0.2 | 熵正則化係數 |

## 🚀 使用方法

### 1. 準備獎勵函數

```python
# 將 reward_function.py 中的代碼複製到 AWS DeepRacer 控制台
```

### 2. 配置訓練參數

在 AWS DeepRacer 控制台中設定：

1. 選擇 **Forever Raceway - Counterclockwise** 環境
2. 設定 **Continuous** action space
3. 配置速度範圍: `0.5 - 3.5 m/s`
4. 配置轉向角度: `-30° 到 30°`
5. 選擇 **SAC** 演算法
6. 套用上述超參數配置

### 3. 開始訓練

建議訓練時間：
- **初始訓練**: 2-3 小時
- **微調優化**: 額外 1-2 小時

### 4. 評估與調整

監控以下指標：
- 完成圈百分比
- 平均圈速
- 出軌次數
- 獎勵收斂情況

## 📈 訓練建議

### 階段一：探索階段 (前 30 分鐘)
- 讓模型探索賽道
- 預期出軌率較高
- 觀察速度選擇傾向

### 階段二：優化階段 (30-90 分鐘)
- 模型開始完成完整圈
- 圈速逐漸下降
- 調整超參數微調

### 階段三：穩定階段 (90 分鐘後)
- 圈速穩定
- 完成率 > 90%
- 考慮 clone 模型繼續訓練

## 🔧 進階調整

### 超參數調整建議

如果遇到以下情況：

**收斂過慢**
```yaml
Learning rate: 0.0003 → 0.0005
Batch size: 64 → 128
```

**過度探索**
```yaml
SAC alpha: 0.2 → 0.1
```

**訓練不穩定**
```yaml
Discount factor: 0.999 → 0.995
Learning rate: 0.0003 → 0.0001
```

## 📊 獎勵函數關鍵參數

```python
# 賽道曲率判斷閾值
STRAIGHT_THRESHOLD = 5°
MILD_TURN_THRESHOLD = 15°

# 速度範圍
MAX_SPEED = 3.0 m/s
MIN_SPEED = 0.5 m/s

# 轉向閾值
STEERING_THRESHOLD = 20°

# 前瞻距離
LOOK_AHEAD_WAYPOINTS = 5
```

## 🛠️ 故障排除

### 常見問題

**Q: 模型頻繁出軌**
- 降低彎道速度獎勵
- 增加中心線獎勵權重
- 調整 `is_sharp_turn` 的速度上限

**Q: 直道速度不夠快**
- 提高直道速度獎勵
- 調整 `optimal_speed` 為 3.0 m/s
- 確認速度範圍設定正確

**Q: 轉彎不順暢**
- 增加轉向平滑度獎勵
- 調整 racing line 寬度
- 檢查方向對齊邏輯

## 📝 版本歷史

- **v1.0** - 初始版本，基礎獎勵函數
- **v2.0** - 加入動態速度策略和曲率計算
- **v3.0** - 優化超參數配置，達成 11 秒圈速


## 🔗 相關資源

- [AWS DeepRacer 官方文檔](https://docs.aws.amazon.com/deepracer/)
- [SAC 演算法論文](https://arxiv.org/abs/1801.01290)
- [強化學習最佳實踐](https://docs.aws.amazon.com/deepracer/latest/developerguide/deepracer-how-it-works.html)
