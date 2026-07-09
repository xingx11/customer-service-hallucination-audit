# 客服回复幻觉检测报告

## 总体指标

| 指标 | 值 |
| --- | --- |
| 样本数 | 20 |
| True Positive | 18 |
| False Positive | 0 |
| True Negative | 2 |
| False Negative | 0 |
| Precision | 1.000 |
| Recall | 1.000 |
| F1 | 1.000 |
| Accuracy | 1.000 |

## 分类结果

| 样本 ID | 是否幻觉 | 幻觉类型 | 触发规则 | 原因 |
| --- | --- | --- | --- | --- |
| h01 | 是 | 政策编造 | policy.return_window_fabrication | 回复把7天无理由退货扩展为30天无理由退货，并承诺商家承担非质量问题运费。 |
| h02 | 是 | 参数编造 | parameter.bluetooth_fabrication | 回复把蓝牙版本、连接能力或延迟参数说成与知识库不一致的更高配置。 |
| h03 | 是 | 能力越界 | capability.logistics_lookup | 客服系统未接入物流查询接口，回复却声称查到包裹位置和送达时间。 |
| h04 | 是 | 政策偏差 | policy.invoice_deviation | 回复声称支持纸质发票或错误申请入口，与仅支持电子发票且需在订单详情页申请的政策不一致。 |
| h05 | 是 | 优惠编造 | discount.coupon_fabrication | 回复承诺了知识库明确不存在的优惠券或优惠活动。 |
| h06 | 是 | 参数编造 | parameter.material_warranty_fabrication | 回复把PU合成革或6个月保修编造为头层牛皮或两年保修。 |
| h07 | 是 | 信息编造 | information.return_address_fabrication | 知识库要求退货地址由系统匹配并短信发送，回复却口头编造具体退货地址和收件人。 |
| h08 | 是 | 政策偏差 | policy.shipping_deviation | 回复的发货时效或快递公司与知识库政策不一致。 |
| h09 | 是 | 参数编造 | parameter.nfc_unsupported | 知识库未标注NFC功能，回复却肯定支持并扩展具体用途。 |
| h10 | 是 | 能力越界 | capability.refund_lookup | 客服系统未接入退款进度查询接口，回复却声称查到退款状态和到账时间。 |
| h11 | 是 | 信息编造 | information.offline_store_fabrication | 知识库说明品牌无线下门店，回复却编造线下体验店或门店查询入口。 |
| h12 | 否 | - | - | 未触发确定性幻觉规则。 |
| h13 | 是 | 安全误导 | safety.pregnancy_guidance | 知识库要求孕妇或哺乳期女性咨询医生，回复却建议放心使用。 |
| h14 | 是 | 能力越界 | capability.order_modify | 客服系统未接入订单修改接口，回复却声称已经修改收货地址。 |
| h15 | 是 | 信息编造 | information.brand_relation_fabrication | 知识库未提及品牌关联关系，回复却编造子品牌、供应链或品控关联。 |
| h16 | 否 | - | - | 未触发确定性幻觉规则。 |
| h17 | 是 | 参数编造 | parameter.connector_fabrication | 知识库标注充电头为USB-A输出，回复却说成Type-C接口。 |
| h18 | 是 | 能力越界 | capability.ticket_escalation | 客服系统不具备工单升级功能，回复却声称已升级并承诺专属客服处理。 |
| h19 | 是 | 优惠编造 | discount.student_discount_fabrication | 回复编造了当前不存在的学生优惠或学生认证入口。 |
| h20 | 是 | 信息遗漏 | omission.size_feedback | 知识库包含用户反馈偏大半码和选小建议，回复却概括为尺码标准不偏。 |

## 漏检

- 无

## 误报

- 无

## 类型错误

- 无

## 高风险案例

- 无

## 局限性

- 当前报告基于离线确定性规则，无法覆盖所有客服回复表达变体。
- 人工真值只用于评估和错误分析，不参与检测器预测。
- 高风险案例按漏检和安全误导相关错误保守筛选，后续可结合业务风险继续细化。
