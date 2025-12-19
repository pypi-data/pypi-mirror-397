#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Huawei Technologies Co., Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ===========================================================================


class PrefillConfig:
    """
    Prefill配置类

    Attributes:
        maxSeqLen (int): 最大序列长度
        maxInputTokenLen (int): 最大输入token长度
        dp (int): 数据并行度
        cp (int): 上下文并行度
        tp (int): 张量并行度
        sp (int): 序列并行度
        pp (int): 流水线并行度
        moe_ep (int): MoE专家并行度
        moe_tp (int): MoE张量并行度
        ep_level (int): 专家并行级别
        MTP (bool): MTP配置状态(true或false)
        maxPrefillTokens (int): 最大预填充token数
        enable_init_routing_cutoff (bool): 是否启用初始路由截断（a910b）
        topk_scaling_factor (float): topk缩放因子（a910b）
    """

    def __init__(self, maxSeqLen, maxInputTokenLen, dp, cp, tp, sp, pp, moe_ep,
                 moe_tp, ep_level, MTP, maxPrefillTokens,
                 enable_init_routing_cutoff=None, topk_scaling_factor=None):
        # type: (int, int, int, int, int, int, int, int, int, int, bool, int, bool, float) -> None
        self.maxSeqLen = maxSeqLen              # type: int
        self.maxInputTokenLen = maxInputTokenLen  # type: int
        self.dp = dp                            # type: int
        self.cp = cp                            # type: int
        self.tp = tp                            # type: int
        self.sp = sp                            # type: int
        self.pp = pp                            # type: int
        self.moe_ep = moe_ep                    # type: int
        self.moe_tp = moe_tp                    # type: int
        self.ep_level = ep_level                # type: int
        self.MTP = MTP                          # type: bool
        self.maxPrefillTokens = maxPrefillTokens  # type: int
        self.enable_init_routing_cutoff = enable_init_routing_cutoff  # type: bool
        self.topk_scaling_factor = topk_scaling_factor  # type: float


class DecodeConfig:
    """
    Decode配置类

    Attributes:
        maxSeqLen (int): 最大序列长度
        maxInputTokenLen (int): 最大输入token长度
        dp (dict): 数据并行度配置，格式为{节点数: 值}
        tp (int): 张量并行度
        sp (int): 序列并行度
        cp (int): 上下文并行度
        pp (int): 流水线并行度
        moe_ep (dict): MoE专家并行度配置，格式为{节点数: 值}
        moe_tp (int): MoE张量并行度
        ep_level (int): 专家并行级别
        MTP (bool): MTP配置状态("开启"或"关闭")
        maxPrefillTokens (int): 最大预填充token数
        maxIterTimes (int): 最大迭代次数
    """

    def __init__(self, maxSeqLen, maxInputTokenLen, dp, tp, sp, cp, pp, moe_ep,
                 moe_tp, ep_level, MTP, maxPrefillTokens, maxIterTimes):
        # type: (int, int, dict, int, int, int, int, dict, int, int, bool, int, int) -> None
        self.maxSeqLen = maxSeqLen              # type: int
        self.maxInputTokenLen = maxInputTokenLen  # type: int
        self.dp = dp                            # type: dict
        self.tp = tp                            # type: int
        self.sp = sp                            # type: int
        self.cp = cp                            # type: int
        self.pp = pp                            # type: int
        self.moe_ep = moe_ep                    # type: dict
        self.moe_tp = moe_tp                    # type: int
        self.ep_level = ep_level                # type: int
        self.MTP = MTP                          # type: bool
        self.maxPrefillTokens = maxPrefillTokens  # type: int
        self.maxIterTimes = maxIterTimes        # type: int


MAX_SEQ_LEN_DICT = {
    18000: "16k",
    68000: "64k",
    134000: "128k",
}

# a910_93 经典配置
STATIC_CONFIG_DICT_A910_93 = {
    "16k": {
        "prefill": PrefillConfig(
            maxSeqLen=18000,           # 最大序列长度
            maxInputTokenLen=18000,    # 最大输入token长度
            dp=2,                      # 数据并行度
            cp=1,                      # 上下文并行度
            tp=8,                      # 张量并行度
            sp=1,                      # 序列并行度
            pp=1,                      # 流水线并行度
            moe_ep=16,                 # MoE专家并行度
            moe_tp=1,                  # MoE张量并行度
            ep_level=2,                # 专家并行级别
            MTP=True,                # MTP配置状态
            maxPrefillTokens=18000     # 最大预填充token数
        ),
        "decode": DecodeConfig(
            maxSeqLen=18000,           # 最大序列长度
            maxInputTokenLen=18000,    # 最大输入token长度
            dp={2: 32, 4: 64, 8: 128},        # 数据并行度配置 {节点数: 值}
            tp=1,                      # 张量并行度
            sp=1,                      # 序列并行度
            cp=1,                      # 上下文并行度
            pp=1,                      # 流水线并行度
            moe_ep={2: 32, 4: 64, 8: 128},    # MoE专家并行度配置 {节点数: 值}
            moe_tp=1,                  # MoE张量并行度
            ep_level=2,                # 专家并行级别
            MTP=True,                # MTP配置状态
            maxPrefillTokens=18000,    # 最大预填充token数
            maxIterTimes=18000         # 最大迭代次数
        )
    },
    "64k": {
        "prefill": PrefillConfig(
            maxSeqLen=68000,
            maxInputTokenLen=68000,
            dp=1,
            cp=2,
            tp=8,
            sp=8,
            pp=1,
            moe_ep=16,
            moe_tp=1,
            ep_level=2,
            MTP=True,
            maxPrefillTokens=68000
        ),
        "decode": DecodeConfig(
            maxSeqLen=68000,
            maxInputTokenLen=68000,
            dp={2: 32, 4: 64, 8: 128},
            tp=1,
            sp=1,
            cp=1,
            pp=1,
            moe_ep={2: 32, 4: 64, 8: 128},
            moe_tp=1,
            ep_level=2,
            MTP=True,
            maxPrefillTokens=68000,
            maxIterTimes=68000
        )
    },
    "128k": {
        "prefill": PrefillConfig(
            maxSeqLen=134000,
            maxInputTokenLen=134000,
            dp=1,
            cp=2,
            tp=8,
            sp=8,
            pp=1,
            moe_ep=16,
            moe_tp=1,
            ep_level=2,
            MTP=False,
            maxPrefillTokens=134000
        ),
        "decode": DecodeConfig(
            maxSeqLen=134000,
            maxInputTokenLen=134000,
            dp={2: 32, 4: 64, 8: 128},
            tp=1,
            sp=1,
            cp=1,
            pp=1,
            moe_ep={2: 32, 4: 64, 8: 128},
            moe_tp=1,
            ep_level=2,
            MTP=False,
            maxPrefillTokens=134000,
            maxIterTimes=134000
        )
    }
}

STATIC_CONFIG_DICT_A910B = {
    "16k": {
        "prefill": PrefillConfig(
            maxSeqLen=18000,           # 最大序列长度
            maxInputTokenLen=18000,    # 最大输入token长度
            dp=2,                      # 数据并行度
            cp=1,                      # 上下文并行度
            tp=8,                      # 张量并行度
            sp=1,                      # 序列并行度
            pp=1,                      # 流水线并行度
            moe_ep=4,                 # MoE专家并行度
            moe_tp=4,                  # MoE张量并行度
            ep_level=1,                # 专家并行级别
            MTP=True,                # MTP配置状态
            enable_init_routing_cutoff=False, # 初始路由剪裁使能
            maxPrefillTokens=18000     # 最大预填充token数
        ),
        "decode": DecodeConfig(
            maxSeqLen=18000,           # 最大序列长度
            maxInputTokenLen=18000,    # 最大输入token长度
            dp={4: 32, 8: 64},        # 数据并行度配置 {节点数: 值}
            tp=1,                      # 张量并行度
            sp=1,                      # 序列并行度
            cp=1,                      # 上下文并行度
            pp=1,                      # 流水线并行度
            moe_ep={4: 32, 8: 64},    # MoE专家并行度配置 {节点数: 值}
            moe_tp=1,                  # MoE张量并行度
            ep_level=2,                # 专家并行级别
            MTP=True,                # MTP配置状态
            maxPrefillTokens=18000,    # 最大预填充token数
            maxIterTimes=18000         # 最大迭代次数
        )
    },
    "64k": {
        "prefill": PrefillConfig(
            maxSeqLen=68000,
            maxInputTokenLen=68000,
            dp=1,
            cp=2,
            tp=8,
            sp=8,
            pp=1,
            moe_ep=16,
            moe_tp=1,
            ep_level=1,
            MTP=True,
            enable_init_routing_cutoff=True,
            topk_scaling_factor=0.25,  # topk缩放因子
            maxPrefillTokens=68000
        ),
        "decode": DecodeConfig(
            maxSeqLen=68000,
            maxInputTokenLen=68000,
            dp={4: 32, 8: 64},
            tp=1,
            sp=1,
            cp=1,
            pp=1,
            moe_ep={4: 32, 8: 64},
            moe_tp=1,
            ep_level=2,
            MTP=True,
            maxPrefillTokens=68000,
            maxIterTimes=68000
        )
    },
    "128k": {
        "prefill": PrefillConfig(
            maxSeqLen=134000,
            maxInputTokenLen=134000,
            dp=1,
            cp=2,
            tp=8,
            sp=8,
            pp=1,
            moe_ep=16,
            moe_tp=1,
            ep_level=1,
            MTP=False,
            enable_init_routing_cutoff=True,
            topk_scaling_factor=0.25,  # topk缩放因子
            maxPrefillTokens=134000
        ),
        "decode": DecodeConfig(
            maxSeqLen=134000,
            maxInputTokenLen=134000,
            dp={4: 32, 8: 64},
            tp=1,
            sp=1,
            cp=1,
            pp=1,
            moe_ep={4: 32, 8: 64},
            moe_tp=1,
            ep_level=2,
            MTP=False,
            maxPrefillTokens=134000,
            maxIterTimes=134000
        )
    }
}

