# 状态、预测转换和目标构造契约

当前方法范围以 [方法搜索与选择](method_search_and_selection.md) 为准：问题固定，算法开放。本文OPD、H/O/C、投影和局部轨迹描述初始候选家族；原experiment_matrix.csv是该家族模板。其它候选的专用步骤/机制门/控制由selected_method和active_experiment_matrix定义，数据隔离、公平预算、独立部署及证据真实性等共同要求保留。

状态：待实现、待验证。此契约优先消除数值和自动微分歧义；实际模型适配必须依据本地代码与官方 scheduler 定义核验。不能仅根据输出张量名字判断参数化。

## 1. 共同状态坐标

定义真正生成区域的 latent `z=α(t)y+σ(t)ε`，其中 `y=x0` 为使用实际 VAE scaling/shift 的干净 latent。对齐 VAE 权重、latent 通道/空间/时间布局、噪声偏移、时间方向、teacher/student scheduler、条件拼接及生成区域 mask。参考 token、固定首帧和其它非生成区域不进入 KD 的范数、投影、梯度或 loss 分母；E_c 与公共身份 loss 也仅聚合预注册的生成评价帧，排除固定帧/重叠参考帧，不能让固定内容伪装成条件保持。VAE 不同且无经验证映射时先停止此平台的直接蒸馏，不能靠 reshape 掩盖不兼容。

CFG、text-negative、guidance rescale 与模型输出预条件也属于预测定义；记录 teacher/student 的实际设置。查清模型返回值是否已是 scheduler 处理后的 denoised 值。不得重复转换。训练和评价必须使用实际 σ 或 log-SNR，而非跨 scheduler 不可比的 step index。

## 2. 转为干净 latent

所有标量以广播的每样本 timestep 计算，操作采用足够精度，禁止零除。设 `A=α²+σ²`：

| 模型原生输出 | 转换为 `y` | 必要条件 |
|---|---|---|
| 干净预测 `ŷ0` | `y=ŷ0` | scaling/shift 与状态一致 |
| 噪声 `ε̂` | `y=(z−σε̂)/α` | `|α|>eps_schedule` |
| 标准 v `v̂=αε−σy` | `y=(αz−σv̂)/A` | `A>eps_schedule`；确认真是该 v 定义 |
| 一般 flow `û=α̇y+σ̇ε` | `y=(σ̇z−σû)/D`，`D=ασ̇−σα̇` | `|D|>eps_schedule`；时间导数相对于模型使用的 t |

线性 rectified-flow 例：`α=1−t, σ=t, u=ε−y`，所以 `y=z−tu`；若模型时间方向相反，必须先变换符号和 scheduler。不要把所有命名 velocity 的输出都当标准 v。

## 3. 将修改后的 y 转回原生目标

噪声目标 `ε*=(z−αy*)/σ`；标准 v 目标 `v*=αε*−σy*`；flow 目标 `u*=α̇y*+σ̇ε*`。直接 x0 模型取 `y*`。这些反向转换要求 `|σ|>eps_schedule`。在边界需要专门经验证的解析极限，否则将该 query 标为不可用并计数，不能夹入任意巨大 target。eps 阈值须按模型尺度与精度预注册，不能在看测试后挑选。

配对分支使用独立加噪的实际 `(x0T,ε,t)` 构造正确原生 label。rollout 后只在新 `zq,tq` 上查询双方并转换；原始 ε 一般不是 `zq` 的标签。

## 4. 条件误差与梯度路径

使用冻结可微 `E_c(y)=D(F(Decode(y)),c)`。Decode 包括正确逆缩放，F 使用其要求的可微 normalization/resize。人脸 detection 与 alignment 坐标可以在 detached 图像估计，再固定坐标用可微 grid sampling 裁剪；梯度路径本身不能经过 PIL/NumPy/ONNX 推理或硬检测器。保存 alignment 有效性、遮挡与裁剪质量，不假定每帧可检测。

query `zq` detached。在 `no_grad` 得到 `yT`；学生 `yS_pred` 保留用于训练的图。令 `yS0=yS_pred.detach()`；创建单独 leaf `yprobe=yS0.clone().requires_grad_(True)`，只算 `g=∂E_c/∂yprobe`，`create_graph=False`。VAE/F 参数冻结，但对输入保留梯度。构造目标前 `g=g.detach()`，目标最终 `y*.detach()`。学生公共 `Lc,q` 可另走一阶训练图；不能误把 detached 的 `yprobe` 当作学生身份 loss。

将 `g`、`d0=yT−yS0` 投影至生成 mask `M`；mask 为 0 的坐标 target 保持 `yS0`，KD 也不计入。按每样本全部有效生成坐标计算内积，不跨 batch 聚合；mask 非空后可使用归一化内积，但投影的分子分母必须用同一规范。

## 5. H1 门控

在相同 query 上检查原始老师目标的实际代理误差 `E_c(yT)≤E_c(yS0)+δ`，且均有限、身份裁剪有效，才接受该样本原始 KD。为公平，H1 的半径规则与 H2 在预注册消融中区分；主定义不得把“门控＋投影”混称纯门控。记录实际采用的是原始 yT 检查还是半径裁剪后的目标检查；推荐主 H1 检查原始 yT，独立报告半径匹配门控消融。

## 6. H2/O1 每样本安全目标

理想问题：尽量靠近 yT，满足 `E_c(y)≤E_c(yS0)+δ` 及 `||M(y−yS0)||≤r`。实际仅使用一阶近似：

`d0=M(yT−yS0)`；若 g 可靠且 `||g||²>eps_grad`，

`d=d0−max(0,<g,d0>)/||g||²·g`。

在 δ>0 时该投影仍采用非增一阶半空间，δ 仅用于实际检查容差；不能把该公式写成已精确求解原始非线性约束。接着用已注册的范数按样本半径裁剪 d，依次试 `a∈{1,1/2,1/4}`，选满足实际、有限的代理误差检查的最大 a。得到 `y*=yS0+a d`，最后转换为原生 target 并 stopgrad。

必须明确定义 `r` 是 raw L2 还是 valid-coordinate RMS，记录 latent 尺度；不同视频长度不能默用同一 raw L2 半径。默认推荐生成区域 RMS 半径，投影内积同样按有效坐标一致归一化。

配置中的 eps_grad 始终以平方范数为单位，可靠与 fallback 使用互补阈值；不把 norm 与 squared norm 混用。

**零梯度 fallback**：若 g 有限但 ||g||²≤eps_grad，不能因“零梯度”直接接受任意老师方向。先使用裁剪后的 d0，仍执行同一实际代理误差回溯；通过才接受，并标记 `zero_grad_checked`，否则拒绝。若 E/F 本身无效、g 非有限、有效 mask 为空或转换不可逆，直接拒绝局部 KD，不走零梯度 fallback。

**每样本拒绝**：所有 a 检查失败、反向转换非有限或身份裁剪无效时，只令该样本 KD 权重为 0；有效配对和公共条件损失继续。有效样本条件 loss 本身失效则单独屏蔽并计数。全 batch KD 拒绝时返回设备/精度正确的零 KD 标量，仍执行有意义的公共更新；若全部 loss 无效则跳过 optimizer/scheduler 步并记 `no_valid_loss`，不能把无操作计为有效训练更新。

拒绝样本采用 `sum(w_i·loss_i)/B`，与 H0 保持固定总 batch 分母，避免接受率低时自动增大单样本 KD 权重；如采用接受数分母须作为显式消融。记录接受率、实际 KD/梯度范数与训练有效更新数。

## 7. 必须分开的结论与验证

投影至多给出可靠 g 下的局部一阶约束；回溯检查只约束被构造 target 的代理误差；有限次拟合和完整采样均无端到端保证。不得将 `g·d≤0` 或 target check PASS 写成身份保持定理。

正式训练前执行：实际 scheduler 下 x0/epsilon/v/flow 正反 round trip；同一 z,t 的双方状态对齐；alpha/sigma 边界；生成 mask；`g=0/NaN`；半个 batch 拒绝/全 batch 拒绝；loss 的梯度只到学生可训练参数且 target/teacher 无梯度；可微裁剪对 y 的非零梯度。至少测试一个真实模型 batch，不能只用模拟函数宣称平台适配成功。

目标诊断保存每样本 `Ec_before/Ec_raw/Ec_target, g_norm, dot_g_d0, projection_norm, target_step, target_radius, accept/reject_reason, mask_count, native_target_finite`；后续 1/5/20 次固定状态拟合及完整生成单独记录。


任务适配：上述身份E_c实例对应T1；T2用可微软边缘误差、T3用可微人体热图/soft-argmax误差，具体见 [three_task_protocol.md](three_task_protocol.md)。T1/T2/T3均遵守相同投影、固定B分母、停止梯度和无效/零梯度处理，但容差与半径按任务校准，不互搬数值。
