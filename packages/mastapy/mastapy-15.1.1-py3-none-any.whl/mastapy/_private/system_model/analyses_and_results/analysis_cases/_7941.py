"""PartAnalysisCase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from PIL.Image import Image

from mastapy._private._internal import conversion, utility
from mastapy._private.system_model.analyses_and_results import _2949

_PART_ANALYSIS_CASE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.AnalysisCases", "PartAnalysisCase"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945
    from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
        _7444,
        _7445,
        _7446,
        _7451,
        _7453,
        _7454,
        _7455,
        _7457,
        _7458,
        _7460,
        _7461,
        _7462,
        _7463,
        _7465,
        _7466,
        _7467,
        _7468,
        _7470,
        _7472,
        _7473,
        _7475,
        _7476,
        _7478,
        _7479,
        _7481,
        _7483,
        _7485,
        _7487,
        _7488,
        _7490,
        _7491,
        _7492,
        _7495,
        _7497,
        _7499,
        _7500,
        _7501,
        _7502,
        _7504,
        _7505,
        _7506,
        _7507,
        _7509,
        _7510,
        _7511,
        _7513,
        _7515,
        _7517,
        _7518,
        _7520,
        _7521,
        _7523,
        _7525,
        _7526,
        _7527,
        _7528,
        _7529,
        _7530,
        _7531,
        _7532,
        _7534,
        _7536,
        _7537,
        _7538,
        _7539,
        _7540,
        _7541,
        _7543,
        _7544,
        _7546,
        _7547,
        _7548,
        _7550,
        _7551,
        _7553,
        _7554,
        _7556,
        _7557,
        _7559,
        _7560,
        _7562,
        _7563,
        _7564,
        _7565,
        _7566,
        _7567,
        _7568,
        _7569,
        _7571,
        _7572,
        _7574,
        _7575,
        _7576,
        _7578,
        _7579,
        _7581,
    )
    from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
        _7176,
        _7177,
        _7178,
        _7184,
        _7186,
        _7187,
        _7189,
        _7191,
        _7192,
        _7194,
        _7195,
        _7196,
        _7197,
        _7199,
        _7200,
        _7201,
        _7202,
        _7204,
        _7206,
        _7207,
        _7209,
        _7210,
        _7212,
        _7213,
        _7215,
        _7217,
        _7218,
        _7220,
        _7221,
        _7223,
        _7224,
        _7225,
        _7228,
        _7230,
        _7231,
        _7232,
        _7233,
        _7234,
        _7236,
        _7237,
        _7238,
        _7239,
        _7241,
        _7242,
        _7244,
        _7246,
        _7248,
        _7250,
        _7251,
        _7253,
        _7254,
        _7256,
        _7257,
        _7258,
        _7259,
        _7260,
        _7261,
        _7262,
        _7263,
        _7264,
        _7266,
        _7268,
        _7269,
        _7270,
        _7271,
        _7272,
        _7273,
        _7275,
        _7276,
        _7278,
        _7279,
        _7280,
        _7282,
        _7283,
        _7285,
        _7286,
        _7288,
        _7289,
        _7291,
        _7292,
        _7294,
        _7295,
        _7296,
        _7297,
        _7298,
        _7299,
        _7300,
        _7301,
        _7303,
        _7304,
        _7305,
        _7306,
        _7307,
        _7309,
        _7310,
        _7312,
    )
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7943,
        _7944,
        _7945,
    )
    from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
        _6911,
        _6912,
        _6913,
        _6915,
        _6917,
        _6918,
        _6919,
        _6921,
        _6922,
        _6924,
        _6925,
        _6926,
        _6927,
        _6929,
        _6930,
        _6931,
        _6933,
        _6934,
        _6936,
        _6938,
        _6939,
        _6940,
        _6942,
        _6943,
        _6945,
        _6947,
        _6949,
        _6950,
        _6955,
        _6956,
        _6957,
        _6959,
        _6961,
        _6963,
        _6964,
        _6965,
        _6966,
        _6967,
        _6969,
        _6970,
        _6971,
        _6972,
        _6974,
        _6975,
        _6976,
        _6978,
        _6980,
        _6982,
        _6983,
        _6985,
        _6986,
        _6988,
        _6989,
        _6990,
        _6991,
        _6992,
        _6993,
        _6994,
        _6995,
        _6997,
        _6998,
        _7000,
        _7001,
        _7002,
        _7003,
        _7004,
        _7005,
        _7007,
        _7009,
        _7010,
        _7011,
        _7012,
        _7014,
        _7015,
        _7017,
        _7019,
        _7020,
        _7021,
        _7023,
        _7024,
        _7026,
        _7027,
        _7028,
        _7029,
        _7030,
        _7031,
        _7032,
        _7034,
        _7035,
        _7036,
        _7037,
        _7038,
        _7039,
        _7041,
        _7042,
        _7044,
    )
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
        _6641,
        _6642,
        _6643,
        _6645,
        _6647,
        _6648,
        _6649,
        _6651,
        _6652,
        _6654,
        _6655,
        _6656,
        _6657,
        _6659,
        _6660,
        _6661,
        _6663,
        _6664,
        _6666,
        _6668,
        _6669,
        _6670,
        _6672,
        _6673,
        _6675,
        _6677,
        _6679,
        _6680,
        _6682,
        _6683,
        _6684,
        _6686,
        _6688,
        _6690,
        _6691,
        _6692,
        _6695,
        _6696,
        _6698,
        _6699,
        _6700,
        _6701,
        _6703,
        _6704,
        _6705,
        _6707,
        _6709,
        _6711,
        _6712,
        _6714,
        _6715,
        _6717,
        _6718,
        _6719,
        _6720,
        _6721,
        _6722,
        _6723,
        _6724,
        _6726,
        _6727,
        _6729,
        _6730,
        _6731,
        _6732,
        _6733,
        _6734,
        _6736,
        _6738,
        _6739,
        _6740,
        _6741,
        _6743,
        _6744,
        _6746,
        _6748,
        _6749,
        _6750,
        _6752,
        _6753,
        _6755,
        _6756,
        _6757,
        _6758,
        _6759,
        _6760,
        _6761,
        _6763,
        _6764,
        _6765,
        _6766,
        _6767,
        _6768,
        _6770,
        _6771,
        _6773,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
        _6020,
        _6022,
        _6023,
        _6025,
        _6027,
        _6028,
        _6029,
        _6031,
        _6032,
        _6034,
        _6035,
        _6036,
        _6037,
        _6039,
        _6040,
        _6041,
        _6043,
        _6044,
        _6047,
        _6049,
        _6050,
        _6051,
        _6053,
        _6054,
        _6056,
        _6058,
        _6060,
        _6061,
        _6063,
        _6064,
        _6065,
        _6067,
        _6069,
        _6071,
        _6072,
        _6074,
        _6089,
        _6090,
        _6092,
        _6093,
        _6094,
        _6096,
        _6101,
        _6103,
        _6116,
        _6118,
        _6120,
        _6122,
        _6123,
        _6125,
        _6126,
        _6128,
        _6129,
        _6130,
        _6131,
        _6132,
        _6134,
        _6135,
        _6136,
        _6138,
        _6139,
        _6142,
        _6143,
        _6144,
        _6145,
        _6146,
        _6148,
        _6150,
        _6152,
        _6153,
        _6154,
        _6155,
        _6158,
        _6160,
        _6162,
        _6164,
        _6165,
        _6167,
        _6169,
        _6170,
        _6172,
        _6173,
        _6174,
        _6175,
        _6176,
        _6177,
        _6178,
        _6180,
        _6181,
        _6182,
        _6184,
        _6185,
        _6186,
        _6188,
        _6189,
        _6191,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
        _6368,
        _6369,
        _6370,
        _6372,
        _6374,
        _6375,
        _6376,
        _6378,
        _6379,
        _6381,
        _6382,
        _6383,
        _6384,
        _6386,
        _6387,
        _6388,
        _6390,
        _6391,
        _6393,
        _6395,
        _6396,
        _6397,
        _6399,
        _6400,
        _6402,
        _6404,
        _6406,
        _6407,
        _6409,
        _6410,
        _6411,
        _6413,
        _6415,
        _6417,
        _6418,
        _6419,
        _6420,
        _6421,
        _6423,
        _6424,
        _6425,
        _6426,
        _6428,
        _6429,
        _6431,
        _6433,
        _6435,
        _6437,
        _6438,
        _6440,
        _6441,
        _6443,
        _6444,
        _6445,
        _6446,
        _6447,
        _6449,
        _6450,
        _6451,
        _6453,
        _6454,
        _6456,
        _6457,
        _6458,
        _6459,
        _6460,
        _6461,
        _6463,
        _6465,
        _6466,
        _6467,
        _6468,
        _6470,
        _6471,
        _6473,
        _6475,
        _6476,
        _6477,
        _6479,
        _6480,
        _6482,
        _6483,
        _6484,
        _6485,
        _6486,
        _6487,
        _6488,
        _6490,
        _6491,
        _6492,
        _6493,
        _6494,
        _6495,
        _6497,
        _6498,
        _6500,
    )
    from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
        _5711,
        _5712,
        _5713,
        _5716,
        _5717,
        _5719,
        _5721,
        _5724,
        _5726,
        _5727,
        _5728,
        _5729,
        _5731,
        _5732,
        _5733,
        _5734,
        _5736,
        _5737,
        _5740,
        _5742,
        _5743,
        _5745,
        _5746,
        _5748,
        _5749,
        _5751,
        _5753,
        _5754,
        _5756,
        _5757,
        _5758,
        _5760,
        _5763,
        _5764,
        _5765,
        _5766,
        _5767,
        _5769,
        _5770,
        _5771,
        _5772,
        _5775,
        _5776,
        _5777,
        _5779,
        _5780,
        _5787,
        _5788,
        _5790,
        _5791,
        _5793,
        _5794,
        _5795,
        _5799,
        _5800,
        _5801,
        _5802,
        _5804,
        _5805,
        _5807,
        _5808,
        _5810,
        _5811,
        _5812,
        _5813,
        _5814,
        _5815,
        _5817,
        _5819,
        _5820,
        _5823,
        _5824,
        _5827,
        _5829,
        _5830,
        _5833,
        _5834,
        _5836,
        _5837,
        _5839,
        _5840,
        _5841,
        _5842,
        _5843,
        _5844,
        _5845,
        _5846,
        _5849,
        _5850,
        _5852,
        _5853,
        _5854,
        _5857,
        _5858,
        _5860,
        _5861,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses import (
        _4894,
        _4895,
        _4896,
        _4899,
        _4900,
        _4901,
        _4902,
        _4904,
        _4906,
        _4907,
        _4908,
        _4909,
        _4911,
        _4912,
        _4913,
        _4914,
        _4916,
        _4917,
        _4919,
        _4921,
        _4922,
        _4924,
        _4925,
        _4927,
        _4928,
        _4930,
        _4933,
        _4934,
        _4936,
        _4937,
        _4938,
        _4940,
        _4943,
        _4944,
        _4945,
        _4946,
        _4950,
        _4952,
        _4953,
        _4954,
        _4955,
        _4958,
        _4959,
        _4960,
        _4962,
        _4963,
        _4966,
        _4967,
        _4969,
        _4970,
        _4972,
        _4973,
        _4974,
        _4975,
        _4976,
        _4977,
        _4983,
        _4985,
        _4987,
        _4989,
        _4990,
        _4992,
        _4993,
        _4994,
        _4995,
        _4996,
        _4997,
        _4999,
        _5001,
        _5002,
        _5003,
        _5004,
        _5007,
        _5009,
        _5010,
        _5012,
        _5013,
        _5015,
        _5016,
        _5018,
        _5019,
        _5020,
        _5021,
        _5022,
        _5023,
        _5024,
        _5025,
        _5027,
        _5028,
        _5029,
        _5030,
        _5031,
        _5036,
        _5037,
        _5039,
        _5040,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
        _5448,
        _5449,
        _5450,
        _5453,
        _5454,
        _5455,
        _5456,
        _5458,
        _5460,
        _5461,
        _5462,
        _5463,
        _5465,
        _5466,
        _5467,
        _5468,
        _5470,
        _5471,
        _5473,
        _5475,
        _5476,
        _5478,
        _5479,
        _5481,
        _5482,
        _5484,
        _5486,
        _5487,
        _5489,
        _5490,
        _5491,
        _5493,
        _5496,
        _5497,
        _5498,
        _5499,
        _5500,
        _5502,
        _5503,
        _5504,
        _5505,
        _5507,
        _5508,
        _5509,
        _5511,
        _5512,
        _5515,
        _5516,
        _5518,
        _5519,
        _5521,
        _5522,
        _5523,
        _5524,
        _5525,
        _5526,
        _5528,
        _5529,
        _5530,
        _5532,
        _5533,
        _5535,
        _5536,
        _5537,
        _5538,
        _5539,
        _5540,
        _5542,
        _5544,
        _5545,
        _5546,
        _5547,
        _5549,
        _5551,
        _5552,
        _5554,
        _5555,
        _5557,
        _5558,
        _5560,
        _5561,
        _5562,
        _5563,
        _5564,
        _5565,
        _5566,
        _5567,
        _5569,
        _5570,
        _5571,
        _5572,
        _5573,
        _5575,
        _5576,
        _5578,
        _5579,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
        _5184,
        _5185,
        _5186,
        _5189,
        _5190,
        _5191,
        _5192,
        _5194,
        _5196,
        _5197,
        _5198,
        _5199,
        _5201,
        _5202,
        _5203,
        _5204,
        _5206,
        _5207,
        _5209,
        _5211,
        _5212,
        _5214,
        _5215,
        _5217,
        _5218,
        _5220,
        _5222,
        _5223,
        _5225,
        _5226,
        _5227,
        _5229,
        _5232,
        _5233,
        _5234,
        _5235,
        _5237,
        _5239,
        _5240,
        _5241,
        _5242,
        _5244,
        _5245,
        _5246,
        _5248,
        _5249,
        _5252,
        _5253,
        _5255,
        _5256,
        _5258,
        _5259,
        _5260,
        _5261,
        _5262,
        _5263,
        _5265,
        _5266,
        _5267,
        _5269,
        _5270,
        _5272,
        _5273,
        _5274,
        _5275,
        _5276,
        _5277,
        _5279,
        _5281,
        _5282,
        _5283,
        _5284,
        _5286,
        _5288,
        _5289,
        _5291,
        _5292,
        _5294,
        _5295,
        _5297,
        _5298,
        _5299,
        _5300,
        _5301,
        _5302,
        _5303,
        _5304,
        _5306,
        _5307,
        _5308,
        _5309,
        _5310,
        _5312,
        _5313,
        _5315,
        _5316,
    )
    from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
        _4613,
        _4614,
        _4615,
        _4618,
        _4619,
        _4620,
        _4621,
        _4623,
        _4625,
        _4626,
        _4627,
        _4628,
        _4630,
        _4631,
        _4632,
        _4633,
        _4635,
        _4636,
        _4638,
        _4640,
        _4641,
        _4643,
        _4644,
        _4646,
        _4647,
        _4649,
        _4651,
        _4652,
        _4654,
        _4655,
        _4656,
        _4658,
        _4661,
        _4662,
        _4663,
        _4664,
        _4672,
        _4674,
        _4675,
        _4676,
        _4677,
        _4679,
        _4680,
        _4681,
        _4683,
        _4684,
        _4687,
        _4688,
        _4690,
        _4691,
        _4693,
        _4694,
        _4695,
        _4696,
        _4697,
        _4698,
        _4700,
        _4701,
        _4713,
        _4715,
        _4716,
        _4718,
        _4719,
        _4720,
        _4721,
        _4722,
        _4723,
        _4725,
        _4727,
        _4728,
        _4729,
        _4730,
        _4732,
        _4734,
        _4735,
        _4737,
        _4738,
        _4740,
        _4741,
        _4743,
        _4744,
        _4745,
        _4746,
        _4747,
        _4748,
        _4749,
        _4750,
        _4752,
        _4753,
        _4754,
        _4755,
        _4756,
        _4758,
        _4759,
        _4761,
        _4762,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import (
        _4345,
        _4346,
        _4347,
        _4350,
        _4351,
        _4352,
        _4353,
        _4355,
        _4357,
        _4358,
        _4359,
        _4360,
        _4362,
        _4363,
        _4364,
        _4365,
        _4367,
        _4368,
        _4370,
        _4372,
        _4373,
        _4375,
        _4376,
        _4378,
        _4379,
        _4381,
        _4383,
        _4384,
        _4386,
        _4387,
        _4388,
        _4391,
        _4394,
        _4395,
        _4396,
        _4397,
        _4398,
        _4400,
        _4401,
        _4404,
        _4405,
        _4407,
        _4408,
        _4409,
        _4411,
        _4412,
        _4415,
        _4416,
        _4418,
        _4419,
        _4421,
        _4422,
        _4423,
        _4424,
        _4425,
        _4426,
        _4427,
        _4428,
        _4429,
        _4431,
        _4432,
        _4434,
        _4435,
        _4436,
        _4439,
        _4440,
        _4441,
        _4443,
        _4445,
        _4446,
        _4447,
        _4448,
        _4450,
        _4452,
        _4453,
        _4455,
        _4456,
        _4458,
        _4459,
        _4461,
        _4462,
        _4463,
        _4464,
        _4465,
        _4466,
        _4467,
        _4468,
        _4471,
        _4472,
        _4473,
        _4474,
        _4475,
        _4477,
        _4478,
        _4480,
        _4481,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses import (
        _4072,
        _4073,
        _4074,
        _4077,
        _4078,
        _4079,
        _4080,
        _4082,
        _4084,
        _4085,
        _4086,
        _4087,
        _4089,
        _4090,
        _4091,
        _4092,
        _4094,
        _4095,
        _4097,
        _4099,
        _4100,
        _4102,
        _4103,
        _4105,
        _4106,
        _4108,
        _4110,
        _4111,
        _4114,
        _4115,
        _4116,
        _4119,
        _4121,
        _4122,
        _4123,
        _4124,
        _4126,
        _4128,
        _4129,
        _4130,
        _4131,
        _4133,
        _4134,
        _4135,
        _4137,
        _4138,
        _4141,
        _4142,
        _4144,
        _4145,
        _4147,
        _4148,
        _4149,
        _4150,
        _4151,
        _4152,
        _4153,
        _4154,
        _4155,
        _4157,
        _4158,
        _4160,
        _4161,
        _4162,
        _4163,
        _4164,
        _4165,
        _4167,
        _4169,
        _4170,
        _4171,
        _4172,
        _4174,
        _4176,
        _4177,
        _4179,
        _4180,
        _4185,
        _4186,
        _4188,
        _4189,
        _4190,
        _4191,
        _4192,
        _4193,
        _4194,
        _4195,
        _4197,
        _4198,
        _4199,
        _4200,
        _4201,
        _4203,
        _4204,
        _4206,
        _4207,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
        _3280,
        _3281,
        _3282,
        _3285,
        _3286,
        _3287,
        _3288,
        _3290,
        _3292,
        _3293,
        _3294,
        _3295,
        _3297,
        _3298,
        _3299,
        _3300,
        _3302,
        _3303,
        _3305,
        _3307,
        _3308,
        _3310,
        _3311,
        _3313,
        _3314,
        _3316,
        _3318,
        _3319,
        _3321,
        _3322,
        _3323,
        _3326,
        _3328,
        _3329,
        _3330,
        _3331,
        _3333,
        _3335,
        _3336,
        _3337,
        _3338,
        _3340,
        _3341,
        _3342,
        _3344,
        _3345,
        _3348,
        _3349,
        _3351,
        _3352,
        _3354,
        _3355,
        _3356,
        _3357,
        _3358,
        _3359,
        _3360,
        _3361,
        _3362,
        _3364,
        _3365,
        _3367,
        _3368,
        _3369,
        _3370,
        _3371,
        _3372,
        _3374,
        _3376,
        _3377,
        _3378,
        _3379,
        _3381,
        _3383,
        _3384,
        _3386,
        _3387,
        _3392,
        _3393,
        _3395,
        _3396,
        _3397,
        _3398,
        _3399,
        _3400,
        _3401,
        _3402,
        _3404,
        _3405,
        _3406,
        _3407,
        _3408,
        _3410,
        _3411,
        _3413,
        _3414,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
        _3809,
        _3810,
        _3811,
        _3814,
        _3815,
        _3816,
        _3817,
        _3819,
        _3821,
        _3822,
        _3823,
        _3824,
        _3826,
        _3827,
        _3828,
        _3829,
        _3831,
        _3832,
        _3834,
        _3836,
        _3837,
        _3839,
        _3840,
        _3842,
        _3843,
        _3845,
        _3847,
        _3848,
        _3850,
        _3851,
        _3852,
        _3855,
        _3857,
        _3858,
        _3859,
        _3860,
        _3861,
        _3863,
        _3864,
        _3865,
        _3866,
        _3868,
        _3869,
        _3870,
        _3872,
        _3873,
        _3876,
        _3877,
        _3879,
        _3880,
        _3882,
        _3883,
        _3884,
        _3885,
        _3886,
        _3887,
        _3888,
        _3889,
        _3890,
        _3892,
        _3893,
        _3895,
        _3896,
        _3897,
        _3898,
        _3899,
        _3900,
        _3902,
        _3904,
        _3905,
        _3906,
        _3907,
        _3909,
        _3911,
        _3912,
        _3914,
        _3915,
        _3918,
        _3919,
        _3921,
        _3922,
        _3923,
        _3924,
        _3925,
        _3926,
        _3927,
        _3928,
        _3930,
        _3931,
        _3932,
        _3933,
        _3934,
        _3936,
        _3937,
        _3939,
        _3940,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
        _3546,
        _3547,
        _3548,
        _3551,
        _3552,
        _3553,
        _3554,
        _3556,
        _3558,
        _3559,
        _3560,
        _3561,
        _3563,
        _3564,
        _3565,
        _3566,
        _3568,
        _3569,
        _3571,
        _3573,
        _3574,
        _3576,
        _3577,
        _3579,
        _3580,
        _3582,
        _3584,
        _3585,
        _3587,
        _3588,
        _3589,
        _3592,
        _3594,
        _3595,
        _3596,
        _3597,
        _3598,
        _3600,
        _3601,
        _3602,
        _3603,
        _3605,
        _3606,
        _3607,
        _3609,
        _3610,
        _3613,
        _3614,
        _3616,
        _3617,
        _3619,
        _3620,
        _3621,
        _3622,
        _3623,
        _3624,
        _3625,
        _3626,
        _3627,
        _3629,
        _3630,
        _3632,
        _3633,
        _3634,
        _3635,
        _3636,
        _3637,
        _3639,
        _3641,
        _3642,
        _3643,
        _3644,
        _3646,
        _3648,
        _3649,
        _3651,
        _3652,
        _3655,
        _3656,
        _3658,
        _3659,
        _3660,
        _3661,
        _3662,
        _3663,
        _3664,
        _3665,
        _3667,
        _3668,
        _3669,
        _3670,
        _3671,
        _3673,
        _3674,
        _3676,
        _3677,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2977,
        _2978,
        _2979,
        _2982,
        _2983,
        _2984,
        _2990,
        _2992,
        _2994,
        _2995,
        _2996,
        _2997,
        _2999,
        _3000,
        _3001,
        _3002,
        _3004,
        _3005,
        _3007,
        _3010,
        _3011,
        _3013,
        _3014,
        _3017,
        _3018,
        _3020,
        _3022,
        _3023,
        _3025,
        _3026,
        _3027,
        _3030,
        _3034,
        _3035,
        _3036,
        _3037,
        _3038,
        _3039,
        _3042,
        _3043,
        _3044,
        _3047,
        _3048,
        _3049,
        _3050,
        _3052,
        _3053,
        _3054,
        _3056,
        _3057,
        _3061,
        _3062,
        _3064,
        _3065,
        _3067,
        _3068,
        _3071,
        _3072,
        _3074,
        _3075,
        _3076,
        _3078,
        _3079,
        _3081,
        _3082,
        _3084,
        _3085,
        _3086,
        _3087,
        _3088,
        _3091,
        _3093,
        _3094,
        _3095,
        _3098,
        _3100,
        _3102,
        _3103,
        _3105,
        _3106,
        _3108,
        _3109,
        _3111,
        _3112,
        _3113,
        _3114,
        _3115,
        _3116,
        _3117,
        _3118,
        _3123,
        _3124,
        _3125,
        _3129,
        _3130,
        _3132,
        _3133,
        _3135,
        _3136,
    )

    Self = TypeVar("Self", bound="PartAnalysisCase")
    CastSelf = TypeVar("CastSelf", bound="PartAnalysisCase._Cast_PartAnalysisCase")


__docformat__ = "restructuredtext en"
__all__ = ("PartAnalysisCase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PartAnalysisCase:
    """Special nested class for casting PartAnalysisCase to subclasses."""

    __parent__: "PartAnalysisCase"

    @property
    def part_analysis(self: "CastSelf") -> "_2949.PartAnalysis":
        return self.__parent__._cast(_2949.PartAnalysis)

    @property
    def design_entity_single_context_analysis(
        self: "CastSelf",
    ) -> "_2945.DesignEntitySingleContextAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2945

        return self.__parent__._cast(_2945.DesignEntitySingleContextAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2943.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2943

        return self.__parent__._cast(_2943.DesignEntityAnalysis)

    @property
    def abstract_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_2977.AbstractAssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2977,
        )

        return self.__parent__._cast(_2977.AbstractAssemblySystemDeflection)

    @property
    def abstract_shaft_or_housing_system_deflection(
        self: "CastSelf",
    ) -> "_2978.AbstractShaftOrHousingSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2978,
        )

        return self.__parent__._cast(_2978.AbstractShaftOrHousingSystemDeflection)

    @property
    def abstract_shaft_system_deflection(
        self: "CastSelf",
    ) -> "_2979.AbstractShaftSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2979,
        )

        return self.__parent__._cast(_2979.AbstractShaftSystemDeflection)

    @property
    def agma_gleason_conical_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_2982.AGMAGleasonConicalGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2982,
        )

        return self.__parent__._cast(_2982.AGMAGleasonConicalGearSetSystemDeflection)

    @property
    def agma_gleason_conical_gear_system_deflection(
        self: "CastSelf",
    ) -> "_2983.AGMAGleasonConicalGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2983,
        )

        return self.__parent__._cast(_2983.AGMAGleasonConicalGearSystemDeflection)

    @property
    def assembly_system_deflection(
        self: "CastSelf",
    ) -> "_2984.AssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2984,
        )

        return self.__parent__._cast(_2984.AssemblySystemDeflection)

    @property
    def bearing_system_deflection(self: "CastSelf") -> "_2990.BearingSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2990,
        )

        return self.__parent__._cast(_2990.BearingSystemDeflection)

    @property
    def belt_drive_system_deflection(
        self: "CastSelf",
    ) -> "_2992.BeltDriveSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2992,
        )

        return self.__parent__._cast(_2992.BeltDriveSystemDeflection)

    @property
    def bevel_differential_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_2994.BevelDifferentialGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2994,
        )

        return self.__parent__._cast(_2994.BevelDifferentialGearSetSystemDeflection)

    @property
    def bevel_differential_gear_system_deflection(
        self: "CastSelf",
    ) -> "_2995.BevelDifferentialGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2995,
        )

        return self.__parent__._cast(_2995.BevelDifferentialGearSystemDeflection)

    @property
    def bevel_differential_planet_gear_system_deflection(
        self: "CastSelf",
    ) -> "_2996.BevelDifferentialPlanetGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2996,
        )

        return self.__parent__._cast(_2996.BevelDifferentialPlanetGearSystemDeflection)

    @property
    def bevel_differential_sun_gear_system_deflection(
        self: "CastSelf",
    ) -> "_2997.BevelDifferentialSunGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2997,
        )

        return self.__parent__._cast(_2997.BevelDifferentialSunGearSystemDeflection)

    @property
    def bevel_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_2999.BevelGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2999,
        )

        return self.__parent__._cast(_2999.BevelGearSetSystemDeflection)

    @property
    def bevel_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3000.BevelGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3000,
        )

        return self.__parent__._cast(_3000.BevelGearSystemDeflection)

    @property
    def bolted_joint_system_deflection(
        self: "CastSelf",
    ) -> "_3001.BoltedJointSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3001,
        )

        return self.__parent__._cast(_3001.BoltedJointSystemDeflection)

    @property
    def bolt_system_deflection(self: "CastSelf") -> "_3002.BoltSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3002,
        )

        return self.__parent__._cast(_3002.BoltSystemDeflection)

    @property
    def clutch_half_system_deflection(
        self: "CastSelf",
    ) -> "_3004.ClutchHalfSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3004,
        )

        return self.__parent__._cast(_3004.ClutchHalfSystemDeflection)

    @property
    def clutch_system_deflection(self: "CastSelf") -> "_3005.ClutchSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3005,
        )

        return self.__parent__._cast(_3005.ClutchSystemDeflection)

    @property
    def component_system_deflection(
        self: "CastSelf",
    ) -> "_3007.ComponentSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3007,
        )

        return self.__parent__._cast(_3007.ComponentSystemDeflection)

    @property
    def concept_coupling_half_system_deflection(
        self: "CastSelf",
    ) -> "_3010.ConceptCouplingHalfSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3010,
        )

        return self.__parent__._cast(_3010.ConceptCouplingHalfSystemDeflection)

    @property
    def concept_coupling_system_deflection(
        self: "CastSelf",
    ) -> "_3011.ConceptCouplingSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3011,
        )

        return self.__parent__._cast(_3011.ConceptCouplingSystemDeflection)

    @property
    def concept_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3013.ConceptGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3013,
        )

        return self.__parent__._cast(_3013.ConceptGearSetSystemDeflection)

    @property
    def concept_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3014.ConceptGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3014,
        )

        return self.__parent__._cast(_3014.ConceptGearSystemDeflection)

    @property
    def conical_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3017.ConicalGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3017,
        )

        return self.__parent__._cast(_3017.ConicalGearSetSystemDeflection)

    @property
    def conical_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3018.ConicalGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3018,
        )

        return self.__parent__._cast(_3018.ConicalGearSystemDeflection)

    @property
    def connector_system_deflection(
        self: "CastSelf",
    ) -> "_3020.ConnectorSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3020,
        )

        return self.__parent__._cast(_3020.ConnectorSystemDeflection)

    @property
    def coupling_half_system_deflection(
        self: "CastSelf",
    ) -> "_3022.CouplingHalfSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3022,
        )

        return self.__parent__._cast(_3022.CouplingHalfSystemDeflection)

    @property
    def coupling_system_deflection(
        self: "CastSelf",
    ) -> "_3023.CouplingSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3023,
        )

        return self.__parent__._cast(_3023.CouplingSystemDeflection)

    @property
    def cvt_pulley_system_deflection(
        self: "CastSelf",
    ) -> "_3025.CVTPulleySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3025,
        )

        return self.__parent__._cast(_3025.CVTPulleySystemDeflection)

    @property
    def cvt_system_deflection(self: "CastSelf") -> "_3026.CVTSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3026,
        )

        return self.__parent__._cast(_3026.CVTSystemDeflection)

    @property
    def cycloidal_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_3027.CycloidalAssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3027,
        )

        return self.__parent__._cast(_3027.CycloidalAssemblySystemDeflection)

    @property
    def cycloidal_disc_system_deflection(
        self: "CastSelf",
    ) -> "_3030.CycloidalDiscSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3030,
        )

        return self.__parent__._cast(_3030.CycloidalDiscSystemDeflection)

    @property
    def cylindrical_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3034.CylindricalGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3034,
        )

        return self.__parent__._cast(_3034.CylindricalGearSetSystemDeflection)

    @property
    def cylindrical_gear_set_system_deflection_timestep(
        self: "CastSelf",
    ) -> "_3035.CylindricalGearSetSystemDeflectionTimestep":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3035,
        )

        return self.__parent__._cast(_3035.CylindricalGearSetSystemDeflectionTimestep)

    @property
    def cylindrical_gear_set_system_deflection_with_ltca_results(
        self: "CastSelf",
    ) -> "_3036.CylindricalGearSetSystemDeflectionWithLTCAResults":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3036,
        )

        return self.__parent__._cast(
            _3036.CylindricalGearSetSystemDeflectionWithLTCAResults
        )

    @property
    def cylindrical_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3037.CylindricalGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3037,
        )

        return self.__parent__._cast(_3037.CylindricalGearSystemDeflection)

    @property
    def cylindrical_gear_system_deflection_timestep(
        self: "CastSelf",
    ) -> "_3038.CylindricalGearSystemDeflectionTimestep":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3038,
        )

        return self.__parent__._cast(_3038.CylindricalGearSystemDeflectionTimestep)

    @property
    def cylindrical_gear_system_deflection_with_ltca_results(
        self: "CastSelf",
    ) -> "_3039.CylindricalGearSystemDeflectionWithLTCAResults":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3039,
        )

        return self.__parent__._cast(
            _3039.CylindricalGearSystemDeflectionWithLTCAResults
        )

    @property
    def cylindrical_planet_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3042.CylindricalPlanetGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3042,
        )

        return self.__parent__._cast(_3042.CylindricalPlanetGearSystemDeflection)

    @property
    def datum_system_deflection(self: "CastSelf") -> "_3043.DatumSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3043,
        )

        return self.__parent__._cast(_3043.DatumSystemDeflection)

    @property
    def external_cad_model_system_deflection(
        self: "CastSelf",
    ) -> "_3044.ExternalCADModelSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3044,
        )

        return self.__parent__._cast(_3044.ExternalCADModelSystemDeflection)

    @property
    def face_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3047.FaceGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3047,
        )

        return self.__parent__._cast(_3047.FaceGearSetSystemDeflection)

    @property
    def face_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3048.FaceGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3048,
        )

        return self.__parent__._cast(_3048.FaceGearSystemDeflection)

    @property
    def fe_part_system_deflection(self: "CastSelf") -> "_3049.FEPartSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3049,
        )

        return self.__parent__._cast(_3049.FEPartSystemDeflection)

    @property
    def flexible_pin_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_3050.FlexiblePinAssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3050,
        )

        return self.__parent__._cast(_3050.FlexiblePinAssemblySystemDeflection)

    @property
    def gear_set_system_deflection(self: "CastSelf") -> "_3052.GearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3052,
        )

        return self.__parent__._cast(_3052.GearSetSystemDeflection)

    @property
    def gear_system_deflection(self: "CastSelf") -> "_3053.GearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3053,
        )

        return self.__parent__._cast(_3053.GearSystemDeflection)

    @property
    def guide_dxf_model_system_deflection(
        self: "CastSelf",
    ) -> "_3054.GuideDxfModelSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3054,
        )

        return self.__parent__._cast(_3054.GuideDxfModelSystemDeflection)

    @property
    def hypoid_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3056.HypoidGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3056,
        )

        return self.__parent__._cast(_3056.HypoidGearSetSystemDeflection)

    @property
    def hypoid_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3057.HypoidGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3057,
        )

        return self.__parent__._cast(_3057.HypoidGearSystemDeflection)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3061.KlingelnbergCycloPalloidConicalGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3061,
        )

        return self.__parent__._cast(
            _3061.KlingelnbergCycloPalloidConicalGearSetSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3062.KlingelnbergCycloPalloidConicalGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3062,
        )

        return self.__parent__._cast(
            _3062.KlingelnbergCycloPalloidConicalGearSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3064.KlingelnbergCycloPalloidHypoidGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3064,
        )

        return self.__parent__._cast(
            _3064.KlingelnbergCycloPalloidHypoidGearSetSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3065.KlingelnbergCycloPalloidHypoidGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3065,
        )

        return self.__parent__._cast(
            _3065.KlingelnbergCycloPalloidHypoidGearSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3067.KlingelnbergCycloPalloidSpiralBevelGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3067,
        )

        return self.__parent__._cast(
            _3067.KlingelnbergCycloPalloidSpiralBevelGearSetSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3068.KlingelnbergCycloPalloidSpiralBevelGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3068,
        )

        return self.__parent__._cast(
            _3068.KlingelnbergCycloPalloidSpiralBevelGearSystemDeflection
        )

    @property
    def mass_disc_system_deflection(
        self: "CastSelf",
    ) -> "_3071.MassDiscSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3071,
        )

        return self.__parent__._cast(_3071.MassDiscSystemDeflection)

    @property
    def measurement_component_system_deflection(
        self: "CastSelf",
    ) -> "_3072.MeasurementComponentSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3072,
        )

        return self.__parent__._cast(_3072.MeasurementComponentSystemDeflection)

    @property
    def microphone_array_system_deflection(
        self: "CastSelf",
    ) -> "_3074.MicrophoneArraySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3074,
        )

        return self.__parent__._cast(_3074.MicrophoneArraySystemDeflection)

    @property
    def microphone_system_deflection(
        self: "CastSelf",
    ) -> "_3075.MicrophoneSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3075,
        )

        return self.__parent__._cast(_3075.MicrophoneSystemDeflection)

    @property
    def mountable_component_system_deflection(
        self: "CastSelf",
    ) -> "_3076.MountableComponentSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3076,
        )

        return self.__parent__._cast(_3076.MountableComponentSystemDeflection)

    @property
    def oil_seal_system_deflection(self: "CastSelf") -> "_3078.OilSealSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3078,
        )

        return self.__parent__._cast(_3078.OilSealSystemDeflection)

    @property
    def part_system_deflection(self: "CastSelf") -> "_3079.PartSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3079,
        )

        return self.__parent__._cast(_3079.PartSystemDeflection)

    @property
    def part_to_part_shear_coupling_half_system_deflection(
        self: "CastSelf",
    ) -> "_3081.PartToPartShearCouplingHalfSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3081,
        )

        return self.__parent__._cast(_3081.PartToPartShearCouplingHalfSystemDeflection)

    @property
    def part_to_part_shear_coupling_system_deflection(
        self: "CastSelf",
    ) -> "_3082.PartToPartShearCouplingSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3082,
        )

        return self.__parent__._cast(_3082.PartToPartShearCouplingSystemDeflection)

    @property
    def planet_carrier_system_deflection(
        self: "CastSelf",
    ) -> "_3084.PlanetCarrierSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3084,
        )

        return self.__parent__._cast(_3084.PlanetCarrierSystemDeflection)

    @property
    def point_load_system_deflection(
        self: "CastSelf",
    ) -> "_3085.PointLoadSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3085,
        )

        return self.__parent__._cast(_3085.PointLoadSystemDeflection)

    @property
    def power_load_system_deflection(
        self: "CastSelf",
    ) -> "_3086.PowerLoadSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3086,
        )

        return self.__parent__._cast(_3086.PowerLoadSystemDeflection)

    @property
    def pulley_system_deflection(self: "CastSelf") -> "_3087.PulleySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3087,
        )

        return self.__parent__._cast(_3087.PulleySystemDeflection)

    @property
    def ring_pins_system_deflection(
        self: "CastSelf",
    ) -> "_3088.RingPinsSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3088,
        )

        return self.__parent__._cast(_3088.RingPinsSystemDeflection)

    @property
    def rolling_ring_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_3091.RollingRingAssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3091,
        )

        return self.__parent__._cast(_3091.RollingRingAssemblySystemDeflection)

    @property
    def rolling_ring_system_deflection(
        self: "CastSelf",
    ) -> "_3093.RollingRingSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3093,
        )

        return self.__parent__._cast(_3093.RollingRingSystemDeflection)

    @property
    def root_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_3094.RootAssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3094,
        )

        return self.__parent__._cast(_3094.RootAssemblySystemDeflection)

    @property
    def shaft_hub_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3095.ShaftHubConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3095,
        )

        return self.__parent__._cast(_3095.ShaftHubConnectionSystemDeflection)

    @property
    def shaft_system_deflection(self: "CastSelf") -> "_3098.ShaftSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3098,
        )

        return self.__parent__._cast(_3098.ShaftSystemDeflection)

    @property
    def specialised_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_3100.SpecialisedAssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3100,
        )

        return self.__parent__._cast(_3100.SpecialisedAssemblySystemDeflection)

    @property
    def spiral_bevel_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3102.SpiralBevelGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3102,
        )

        return self.__parent__._cast(_3102.SpiralBevelGearSetSystemDeflection)

    @property
    def spiral_bevel_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3103.SpiralBevelGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3103,
        )

        return self.__parent__._cast(_3103.SpiralBevelGearSystemDeflection)

    @property
    def spring_damper_half_system_deflection(
        self: "CastSelf",
    ) -> "_3105.SpringDamperHalfSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3105,
        )

        return self.__parent__._cast(_3105.SpringDamperHalfSystemDeflection)

    @property
    def spring_damper_system_deflection(
        self: "CastSelf",
    ) -> "_3106.SpringDamperSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3106,
        )

        return self.__parent__._cast(_3106.SpringDamperSystemDeflection)

    @property
    def straight_bevel_diff_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3108.StraightBevelDiffGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3108,
        )

        return self.__parent__._cast(_3108.StraightBevelDiffGearSetSystemDeflection)

    @property
    def straight_bevel_diff_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3109.StraightBevelDiffGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3109,
        )

        return self.__parent__._cast(_3109.StraightBevelDiffGearSystemDeflection)

    @property
    def straight_bevel_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3111.StraightBevelGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3111,
        )

        return self.__parent__._cast(_3111.StraightBevelGearSetSystemDeflection)

    @property
    def straight_bevel_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3112.StraightBevelGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3112,
        )

        return self.__parent__._cast(_3112.StraightBevelGearSystemDeflection)

    @property
    def straight_bevel_planet_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3113.StraightBevelPlanetGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3113,
        )

        return self.__parent__._cast(_3113.StraightBevelPlanetGearSystemDeflection)

    @property
    def straight_bevel_sun_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3114.StraightBevelSunGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3114,
        )

        return self.__parent__._cast(_3114.StraightBevelSunGearSystemDeflection)

    @property
    def synchroniser_half_system_deflection(
        self: "CastSelf",
    ) -> "_3115.SynchroniserHalfSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3115,
        )

        return self.__parent__._cast(_3115.SynchroniserHalfSystemDeflection)

    @property
    def synchroniser_part_system_deflection(
        self: "CastSelf",
    ) -> "_3116.SynchroniserPartSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3116,
        )

        return self.__parent__._cast(_3116.SynchroniserPartSystemDeflection)

    @property
    def synchroniser_sleeve_system_deflection(
        self: "CastSelf",
    ) -> "_3117.SynchroniserSleeveSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3117,
        )

        return self.__parent__._cast(_3117.SynchroniserSleeveSystemDeflection)

    @property
    def synchroniser_system_deflection(
        self: "CastSelf",
    ) -> "_3118.SynchroniserSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3118,
        )

        return self.__parent__._cast(_3118.SynchroniserSystemDeflection)

    @property
    def torque_converter_pump_system_deflection(
        self: "CastSelf",
    ) -> "_3123.TorqueConverterPumpSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3123,
        )

        return self.__parent__._cast(_3123.TorqueConverterPumpSystemDeflection)

    @property
    def torque_converter_system_deflection(
        self: "CastSelf",
    ) -> "_3124.TorqueConverterSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3124,
        )

        return self.__parent__._cast(_3124.TorqueConverterSystemDeflection)

    @property
    def torque_converter_turbine_system_deflection(
        self: "CastSelf",
    ) -> "_3125.TorqueConverterTurbineSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3125,
        )

        return self.__parent__._cast(_3125.TorqueConverterTurbineSystemDeflection)

    @property
    def unbalanced_mass_system_deflection(
        self: "CastSelf",
    ) -> "_3129.UnbalancedMassSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3129,
        )

        return self.__parent__._cast(_3129.UnbalancedMassSystemDeflection)

    @property
    def virtual_component_system_deflection(
        self: "CastSelf",
    ) -> "_3130.VirtualComponentSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3130,
        )

        return self.__parent__._cast(_3130.VirtualComponentSystemDeflection)

    @property
    def worm_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3132.WormGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3132,
        )

        return self.__parent__._cast(_3132.WormGearSetSystemDeflection)

    @property
    def worm_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3133.WormGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3133,
        )

        return self.__parent__._cast(_3133.WormGearSystemDeflection)

    @property
    def zerol_bevel_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3135.ZerolBevelGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3135,
        )

        return self.__parent__._cast(_3135.ZerolBevelGearSetSystemDeflection)

    @property
    def zerol_bevel_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3136.ZerolBevelGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3136,
        )

        return self.__parent__._cast(_3136.ZerolBevelGearSystemDeflection)

    @property
    def abstract_assembly_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3280.AbstractAssemblySteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3280,
        )

        return self.__parent__._cast(
            _3280.AbstractAssemblySteadyStateSynchronousResponse
        )

    @property
    def abstract_shaft_or_housing_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3281.AbstractShaftOrHousingSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3281,
        )

        return self.__parent__._cast(
            _3281.AbstractShaftOrHousingSteadyStateSynchronousResponse
        )

    @property
    def abstract_shaft_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3282.AbstractShaftSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3282,
        )

        return self.__parent__._cast(_3282.AbstractShaftSteadyStateSynchronousResponse)

    @property
    def agma_gleason_conical_gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3285.AGMAGleasonConicalGearSetSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3285,
        )

        return self.__parent__._cast(
            _3285.AGMAGleasonConicalGearSetSteadyStateSynchronousResponse
        )

    @property
    def agma_gleason_conical_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3286.AGMAGleasonConicalGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3286,
        )

        return self.__parent__._cast(
            _3286.AGMAGleasonConicalGearSteadyStateSynchronousResponse
        )

    @property
    def assembly_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3287.AssemblySteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3287,
        )

        return self.__parent__._cast(_3287.AssemblySteadyStateSynchronousResponse)

    @property
    def bearing_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3288.BearingSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3288,
        )

        return self.__parent__._cast(_3288.BearingSteadyStateSynchronousResponse)

    @property
    def belt_drive_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3290.BeltDriveSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3290,
        )

        return self.__parent__._cast(_3290.BeltDriveSteadyStateSynchronousResponse)

    @property
    def bevel_differential_gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3292.BevelDifferentialGearSetSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3292,
        )

        return self.__parent__._cast(
            _3292.BevelDifferentialGearSetSteadyStateSynchronousResponse
        )

    @property
    def bevel_differential_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3293.BevelDifferentialGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3293,
        )

        return self.__parent__._cast(
            _3293.BevelDifferentialGearSteadyStateSynchronousResponse
        )

    @property
    def bevel_differential_planet_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3294.BevelDifferentialPlanetGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3294,
        )

        return self.__parent__._cast(
            _3294.BevelDifferentialPlanetGearSteadyStateSynchronousResponse
        )

    @property
    def bevel_differential_sun_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3295.BevelDifferentialSunGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3295,
        )

        return self.__parent__._cast(
            _3295.BevelDifferentialSunGearSteadyStateSynchronousResponse
        )

    @property
    def bevel_gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3297.BevelGearSetSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3297,
        )

        return self.__parent__._cast(_3297.BevelGearSetSteadyStateSynchronousResponse)

    @property
    def bevel_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3298.BevelGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3298,
        )

        return self.__parent__._cast(_3298.BevelGearSteadyStateSynchronousResponse)

    @property
    def bolted_joint_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3299.BoltedJointSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3299,
        )

        return self.__parent__._cast(_3299.BoltedJointSteadyStateSynchronousResponse)

    @property
    def bolt_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3300.BoltSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3300,
        )

        return self.__parent__._cast(_3300.BoltSteadyStateSynchronousResponse)

    @property
    def clutch_half_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3302.ClutchHalfSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3302,
        )

        return self.__parent__._cast(_3302.ClutchHalfSteadyStateSynchronousResponse)

    @property
    def clutch_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3303.ClutchSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3303,
        )

        return self.__parent__._cast(_3303.ClutchSteadyStateSynchronousResponse)

    @property
    def component_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3305.ComponentSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3305,
        )

        return self.__parent__._cast(_3305.ComponentSteadyStateSynchronousResponse)

    @property
    def concept_coupling_half_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3307.ConceptCouplingHalfSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3307,
        )

        return self.__parent__._cast(
            _3307.ConceptCouplingHalfSteadyStateSynchronousResponse
        )

    @property
    def concept_coupling_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3308.ConceptCouplingSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3308,
        )

        return self.__parent__._cast(
            _3308.ConceptCouplingSteadyStateSynchronousResponse
        )

    @property
    def concept_gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3310.ConceptGearSetSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3310,
        )

        return self.__parent__._cast(_3310.ConceptGearSetSteadyStateSynchronousResponse)

    @property
    def concept_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3311.ConceptGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3311,
        )

        return self.__parent__._cast(_3311.ConceptGearSteadyStateSynchronousResponse)

    @property
    def conical_gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3313.ConicalGearSetSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3313,
        )

        return self.__parent__._cast(_3313.ConicalGearSetSteadyStateSynchronousResponse)

    @property
    def conical_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3314.ConicalGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3314,
        )

        return self.__parent__._cast(_3314.ConicalGearSteadyStateSynchronousResponse)

    @property
    def connector_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3316.ConnectorSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3316,
        )

        return self.__parent__._cast(_3316.ConnectorSteadyStateSynchronousResponse)

    @property
    def coupling_half_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3318.CouplingHalfSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3318,
        )

        return self.__parent__._cast(_3318.CouplingHalfSteadyStateSynchronousResponse)

    @property
    def coupling_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3319.CouplingSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3319,
        )

        return self.__parent__._cast(_3319.CouplingSteadyStateSynchronousResponse)

    @property
    def cvt_pulley_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3321.CVTPulleySteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3321,
        )

        return self.__parent__._cast(_3321.CVTPulleySteadyStateSynchronousResponse)

    @property
    def cvt_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3322.CVTSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3322,
        )

        return self.__parent__._cast(_3322.CVTSteadyStateSynchronousResponse)

    @property
    def cycloidal_assembly_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3323.CycloidalAssemblySteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3323,
        )

        return self.__parent__._cast(
            _3323.CycloidalAssemblySteadyStateSynchronousResponse
        )

    @property
    def cycloidal_disc_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3326.CycloidalDiscSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3326,
        )

        return self.__parent__._cast(_3326.CycloidalDiscSteadyStateSynchronousResponse)

    @property
    def cylindrical_gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3328.CylindricalGearSetSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3328,
        )

        return self.__parent__._cast(
            _3328.CylindricalGearSetSteadyStateSynchronousResponse
        )

    @property
    def cylindrical_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3329.CylindricalGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3329,
        )

        return self.__parent__._cast(
            _3329.CylindricalGearSteadyStateSynchronousResponse
        )

    @property
    def cylindrical_planet_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3330.CylindricalPlanetGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3330,
        )

        return self.__parent__._cast(
            _3330.CylindricalPlanetGearSteadyStateSynchronousResponse
        )

    @property
    def datum_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3331.DatumSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3331,
        )

        return self.__parent__._cast(_3331.DatumSteadyStateSynchronousResponse)

    @property
    def external_cad_model_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3333.ExternalCADModelSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3333,
        )

        return self.__parent__._cast(
            _3333.ExternalCADModelSteadyStateSynchronousResponse
        )

    @property
    def face_gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3335.FaceGearSetSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3335,
        )

        return self.__parent__._cast(_3335.FaceGearSetSteadyStateSynchronousResponse)

    @property
    def face_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3336.FaceGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3336,
        )

        return self.__parent__._cast(_3336.FaceGearSteadyStateSynchronousResponse)

    @property
    def fe_part_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3337.FEPartSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3337,
        )

        return self.__parent__._cast(_3337.FEPartSteadyStateSynchronousResponse)

    @property
    def flexible_pin_assembly_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3338.FlexiblePinAssemblySteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3338,
        )

        return self.__parent__._cast(
            _3338.FlexiblePinAssemblySteadyStateSynchronousResponse
        )

    @property
    def gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3340.GearSetSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3340,
        )

        return self.__parent__._cast(_3340.GearSetSteadyStateSynchronousResponse)

    @property
    def gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3341.GearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3341,
        )

        return self.__parent__._cast(_3341.GearSteadyStateSynchronousResponse)

    @property
    def guide_dxf_model_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3342.GuideDxfModelSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3342,
        )

        return self.__parent__._cast(_3342.GuideDxfModelSteadyStateSynchronousResponse)

    @property
    def hypoid_gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3344.HypoidGearSetSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3344,
        )

        return self.__parent__._cast(_3344.HypoidGearSetSteadyStateSynchronousResponse)

    @property
    def hypoid_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3345.HypoidGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3345,
        )

        return self.__parent__._cast(_3345.HypoidGearSteadyStateSynchronousResponse)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3348.KlingelnbergCycloPalloidConicalGearSetSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3348,
        )

        return self.__parent__._cast(
            _3348.KlingelnbergCycloPalloidConicalGearSetSteadyStateSynchronousResponse
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3349.KlingelnbergCycloPalloidConicalGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3349,
        )

        return self.__parent__._cast(
            _3349.KlingelnbergCycloPalloidConicalGearSteadyStateSynchronousResponse
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3351.KlingelnbergCycloPalloidHypoidGearSetSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3351,
        )

        return self.__parent__._cast(
            _3351.KlingelnbergCycloPalloidHypoidGearSetSteadyStateSynchronousResponse
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3352.KlingelnbergCycloPalloidHypoidGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3352,
        )

        return self.__parent__._cast(
            _3352.KlingelnbergCycloPalloidHypoidGearSteadyStateSynchronousResponse
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> (
        "_3354.KlingelnbergCycloPalloidSpiralBevelGearSetSteadyStateSynchronousResponse"
    ):
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3354,
        )

        return self.__parent__._cast(
            _3354.KlingelnbergCycloPalloidSpiralBevelGearSetSteadyStateSynchronousResponse
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3355.KlingelnbergCycloPalloidSpiralBevelGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3355,
        )

        return self.__parent__._cast(
            _3355.KlingelnbergCycloPalloidSpiralBevelGearSteadyStateSynchronousResponse
        )

    @property
    def mass_disc_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3356.MassDiscSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3356,
        )

        return self.__parent__._cast(_3356.MassDiscSteadyStateSynchronousResponse)

    @property
    def measurement_component_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3357.MeasurementComponentSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3357,
        )

        return self.__parent__._cast(
            _3357.MeasurementComponentSteadyStateSynchronousResponse
        )

    @property
    def microphone_array_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3358.MicrophoneArraySteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3358,
        )

        return self.__parent__._cast(
            _3358.MicrophoneArraySteadyStateSynchronousResponse
        )

    @property
    def microphone_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3359.MicrophoneSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3359,
        )

        return self.__parent__._cast(_3359.MicrophoneSteadyStateSynchronousResponse)

    @property
    def mountable_component_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3360.MountableComponentSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3360,
        )

        return self.__parent__._cast(
            _3360.MountableComponentSteadyStateSynchronousResponse
        )

    @property
    def oil_seal_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3361.OilSealSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3361,
        )

        return self.__parent__._cast(_3361.OilSealSteadyStateSynchronousResponse)

    @property
    def part_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3362.PartSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3362,
        )

        return self.__parent__._cast(_3362.PartSteadyStateSynchronousResponse)

    @property
    def part_to_part_shear_coupling_half_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3364.PartToPartShearCouplingHalfSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3364,
        )

        return self.__parent__._cast(
            _3364.PartToPartShearCouplingHalfSteadyStateSynchronousResponse
        )

    @property
    def part_to_part_shear_coupling_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3365.PartToPartShearCouplingSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3365,
        )

        return self.__parent__._cast(
            _3365.PartToPartShearCouplingSteadyStateSynchronousResponse
        )

    @property
    def planetary_gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3367.PlanetaryGearSetSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3367,
        )

        return self.__parent__._cast(
            _3367.PlanetaryGearSetSteadyStateSynchronousResponse
        )

    @property
    def planet_carrier_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3368.PlanetCarrierSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3368,
        )

        return self.__parent__._cast(_3368.PlanetCarrierSteadyStateSynchronousResponse)

    @property
    def point_load_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3369.PointLoadSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3369,
        )

        return self.__parent__._cast(_3369.PointLoadSteadyStateSynchronousResponse)

    @property
    def power_load_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3370.PowerLoadSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3370,
        )

        return self.__parent__._cast(_3370.PowerLoadSteadyStateSynchronousResponse)

    @property
    def pulley_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3371.PulleySteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3371,
        )

        return self.__parent__._cast(_3371.PulleySteadyStateSynchronousResponse)

    @property
    def ring_pins_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3372.RingPinsSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3372,
        )

        return self.__parent__._cast(_3372.RingPinsSteadyStateSynchronousResponse)

    @property
    def rolling_ring_assembly_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3374.RollingRingAssemblySteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3374,
        )

        return self.__parent__._cast(
            _3374.RollingRingAssemblySteadyStateSynchronousResponse
        )

    @property
    def rolling_ring_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3376.RollingRingSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3376,
        )

        return self.__parent__._cast(_3376.RollingRingSteadyStateSynchronousResponse)

    @property
    def root_assembly_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3377.RootAssemblySteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3377,
        )

        return self.__parent__._cast(_3377.RootAssemblySteadyStateSynchronousResponse)

    @property
    def shaft_hub_connection_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3378.ShaftHubConnectionSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3378,
        )

        return self.__parent__._cast(
            _3378.ShaftHubConnectionSteadyStateSynchronousResponse
        )

    @property
    def shaft_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3379.ShaftSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3379,
        )

        return self.__parent__._cast(_3379.ShaftSteadyStateSynchronousResponse)

    @property
    def specialised_assembly_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3381.SpecialisedAssemblySteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3381,
        )

        return self.__parent__._cast(
            _3381.SpecialisedAssemblySteadyStateSynchronousResponse
        )

    @property
    def spiral_bevel_gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3383.SpiralBevelGearSetSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3383,
        )

        return self.__parent__._cast(
            _3383.SpiralBevelGearSetSteadyStateSynchronousResponse
        )

    @property
    def spiral_bevel_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3384.SpiralBevelGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3384,
        )

        return self.__parent__._cast(
            _3384.SpiralBevelGearSteadyStateSynchronousResponse
        )

    @property
    def spring_damper_half_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3386.SpringDamperHalfSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3386,
        )

        return self.__parent__._cast(
            _3386.SpringDamperHalfSteadyStateSynchronousResponse
        )

    @property
    def spring_damper_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3387.SpringDamperSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3387,
        )

        return self.__parent__._cast(_3387.SpringDamperSteadyStateSynchronousResponse)

    @property
    def straight_bevel_diff_gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3392.StraightBevelDiffGearSetSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3392,
        )

        return self.__parent__._cast(
            _3392.StraightBevelDiffGearSetSteadyStateSynchronousResponse
        )

    @property
    def straight_bevel_diff_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3393.StraightBevelDiffGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3393,
        )

        return self.__parent__._cast(
            _3393.StraightBevelDiffGearSteadyStateSynchronousResponse
        )

    @property
    def straight_bevel_gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3395.StraightBevelGearSetSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3395,
        )

        return self.__parent__._cast(
            _3395.StraightBevelGearSetSteadyStateSynchronousResponse
        )

    @property
    def straight_bevel_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3396.StraightBevelGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3396,
        )

        return self.__parent__._cast(
            _3396.StraightBevelGearSteadyStateSynchronousResponse
        )

    @property
    def straight_bevel_planet_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3397.StraightBevelPlanetGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3397,
        )

        return self.__parent__._cast(
            _3397.StraightBevelPlanetGearSteadyStateSynchronousResponse
        )

    @property
    def straight_bevel_sun_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3398.StraightBevelSunGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3398,
        )

        return self.__parent__._cast(
            _3398.StraightBevelSunGearSteadyStateSynchronousResponse
        )

    @property
    def synchroniser_half_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3399.SynchroniserHalfSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3399,
        )

        return self.__parent__._cast(
            _3399.SynchroniserHalfSteadyStateSynchronousResponse
        )

    @property
    def synchroniser_part_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3400.SynchroniserPartSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3400,
        )

        return self.__parent__._cast(
            _3400.SynchroniserPartSteadyStateSynchronousResponse
        )

    @property
    def synchroniser_sleeve_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3401.SynchroniserSleeveSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3401,
        )

        return self.__parent__._cast(
            _3401.SynchroniserSleeveSteadyStateSynchronousResponse
        )

    @property
    def synchroniser_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3402.SynchroniserSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3402,
        )

        return self.__parent__._cast(_3402.SynchroniserSteadyStateSynchronousResponse)

    @property
    def torque_converter_pump_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3404.TorqueConverterPumpSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3404,
        )

        return self.__parent__._cast(
            _3404.TorqueConverterPumpSteadyStateSynchronousResponse
        )

    @property
    def torque_converter_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3405.TorqueConverterSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3405,
        )

        return self.__parent__._cast(
            _3405.TorqueConverterSteadyStateSynchronousResponse
        )

    @property
    def torque_converter_turbine_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3406.TorqueConverterTurbineSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3406,
        )

        return self.__parent__._cast(
            _3406.TorqueConverterTurbineSteadyStateSynchronousResponse
        )

    @property
    def unbalanced_mass_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3407.UnbalancedMassSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3407,
        )

        return self.__parent__._cast(_3407.UnbalancedMassSteadyStateSynchronousResponse)

    @property
    def virtual_component_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3408.VirtualComponentSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3408,
        )

        return self.__parent__._cast(
            _3408.VirtualComponentSteadyStateSynchronousResponse
        )

    @property
    def worm_gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3410.WormGearSetSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3410,
        )

        return self.__parent__._cast(_3410.WormGearSetSteadyStateSynchronousResponse)

    @property
    def worm_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3411.WormGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3411,
        )

        return self.__parent__._cast(_3411.WormGearSteadyStateSynchronousResponse)

    @property
    def zerol_bevel_gear_set_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3413.ZerolBevelGearSetSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3413,
        )

        return self.__parent__._cast(
            _3413.ZerolBevelGearSetSteadyStateSynchronousResponse
        )

    @property
    def zerol_bevel_gear_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3414.ZerolBevelGearSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3414,
        )

        return self.__parent__._cast(_3414.ZerolBevelGearSteadyStateSynchronousResponse)

    @property
    def abstract_assembly_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3546.AbstractAssemblySteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3546,
        )

        return self.__parent__._cast(
            _3546.AbstractAssemblySteadyStateSynchronousResponseOnAShaft
        )

    @property
    def abstract_shaft_or_housing_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3547.AbstractShaftOrHousingSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3547,
        )

        return self.__parent__._cast(
            _3547.AbstractShaftOrHousingSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def abstract_shaft_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3548.AbstractShaftSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3548,
        )

        return self.__parent__._cast(
            _3548.AbstractShaftSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def agma_gleason_conical_gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3551.AGMAGleasonConicalGearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3551,
        )

        return self.__parent__._cast(
            _3551.AGMAGleasonConicalGearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def agma_gleason_conical_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3552.AGMAGleasonConicalGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3552,
        )

        return self.__parent__._cast(
            _3552.AGMAGleasonConicalGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def assembly_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3553.AssemblySteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3553,
        )

        return self.__parent__._cast(
            _3553.AssemblySteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bearing_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3554.BearingSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3554,
        )

        return self.__parent__._cast(
            _3554.BearingSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def belt_drive_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3556.BeltDriveSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3556,
        )

        return self.__parent__._cast(
            _3556.BeltDriveSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_differential_gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3558.BevelDifferentialGearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3558,
        )

        return self.__parent__._cast(
            _3558.BevelDifferentialGearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_differential_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3559.BevelDifferentialGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3559,
        )

        return self.__parent__._cast(
            _3559.BevelDifferentialGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_differential_planet_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3560.BevelDifferentialPlanetGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3560,
        )

        return self.__parent__._cast(
            _3560.BevelDifferentialPlanetGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_differential_sun_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3561.BevelDifferentialSunGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3561,
        )

        return self.__parent__._cast(
            _3561.BevelDifferentialSunGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3563.BevelGearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3563,
        )

        return self.__parent__._cast(
            _3563.BevelGearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3564.BevelGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3564,
        )

        return self.__parent__._cast(
            _3564.BevelGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bolted_joint_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3565.BoltedJointSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3565,
        )

        return self.__parent__._cast(
            _3565.BoltedJointSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bolt_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3566.BoltSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3566,
        )

        return self.__parent__._cast(_3566.BoltSteadyStateSynchronousResponseOnAShaft)

    @property
    def clutch_half_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3568.ClutchHalfSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3568,
        )

        return self.__parent__._cast(
            _3568.ClutchHalfSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def clutch_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3569.ClutchSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3569,
        )

        return self.__parent__._cast(_3569.ClutchSteadyStateSynchronousResponseOnAShaft)

    @property
    def component_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3571.ComponentSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3571,
        )

        return self.__parent__._cast(
            _3571.ComponentSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def concept_coupling_half_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3573.ConceptCouplingHalfSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3573,
        )

        return self.__parent__._cast(
            _3573.ConceptCouplingHalfSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def concept_coupling_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3574.ConceptCouplingSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3574,
        )

        return self.__parent__._cast(
            _3574.ConceptCouplingSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def concept_gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3576.ConceptGearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3576,
        )

        return self.__parent__._cast(
            _3576.ConceptGearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def concept_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3577.ConceptGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3577,
        )

        return self.__parent__._cast(
            _3577.ConceptGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def conical_gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3579.ConicalGearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3579,
        )

        return self.__parent__._cast(
            _3579.ConicalGearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def conical_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3580.ConicalGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3580,
        )

        return self.__parent__._cast(
            _3580.ConicalGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def connector_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3582.ConnectorSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3582,
        )

        return self.__parent__._cast(
            _3582.ConnectorSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def coupling_half_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3584.CouplingHalfSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3584,
        )

        return self.__parent__._cast(
            _3584.CouplingHalfSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def coupling_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3585.CouplingSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3585,
        )

        return self.__parent__._cast(
            _3585.CouplingSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cvt_pulley_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3587.CVTPulleySteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3587,
        )

        return self.__parent__._cast(
            _3587.CVTPulleySteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cvt_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3588.CVTSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3588,
        )

        return self.__parent__._cast(_3588.CVTSteadyStateSynchronousResponseOnAShaft)

    @property
    def cycloidal_assembly_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3589.CycloidalAssemblySteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3589,
        )

        return self.__parent__._cast(
            _3589.CycloidalAssemblySteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cycloidal_disc_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3592.CycloidalDiscSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3592,
        )

        return self.__parent__._cast(
            _3592.CycloidalDiscSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cylindrical_gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3594.CylindricalGearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3594,
        )

        return self.__parent__._cast(
            _3594.CylindricalGearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cylindrical_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3595.CylindricalGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3595,
        )

        return self.__parent__._cast(
            _3595.CylindricalGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cylindrical_planet_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3596.CylindricalPlanetGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3596,
        )

        return self.__parent__._cast(
            _3596.CylindricalPlanetGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def datum_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3597.DatumSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3597,
        )

        return self.__parent__._cast(_3597.DatumSteadyStateSynchronousResponseOnAShaft)

    @property
    def external_cad_model_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3598.ExternalCADModelSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3598,
        )

        return self.__parent__._cast(
            _3598.ExternalCADModelSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def face_gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3600.FaceGearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3600,
        )

        return self.__parent__._cast(
            _3600.FaceGearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def face_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3601.FaceGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3601,
        )

        return self.__parent__._cast(
            _3601.FaceGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def fe_part_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3602.FEPartSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3602,
        )

        return self.__parent__._cast(_3602.FEPartSteadyStateSynchronousResponseOnAShaft)

    @property
    def flexible_pin_assembly_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3603.FlexiblePinAssemblySteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3603,
        )

        return self.__parent__._cast(
            _3603.FlexiblePinAssemblySteadyStateSynchronousResponseOnAShaft
        )

    @property
    def gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3605.GearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3605,
        )

        return self.__parent__._cast(
            _3605.GearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3606.GearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3606,
        )

        return self.__parent__._cast(_3606.GearSteadyStateSynchronousResponseOnAShaft)

    @property
    def guide_dxf_model_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3607.GuideDxfModelSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3607,
        )

        return self.__parent__._cast(
            _3607.GuideDxfModelSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def hypoid_gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3609.HypoidGearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3609,
        )

        return self.__parent__._cast(
            _3609.HypoidGearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def hypoid_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3610.HypoidGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3610,
        )

        return self.__parent__._cast(
            _3610.HypoidGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3613.KlingelnbergCycloPalloidConicalGearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3613,
        )

        return self.__parent__._cast(
            _3613.KlingelnbergCycloPalloidConicalGearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3614.KlingelnbergCycloPalloidConicalGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3614,
        )

        return self.__parent__._cast(
            _3614.KlingelnbergCycloPalloidConicalGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3616.KlingelnbergCycloPalloidHypoidGearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3616,
        )

        return self.__parent__._cast(
            _3616.KlingelnbergCycloPalloidHypoidGearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> (
        "_3617.KlingelnbergCycloPalloidHypoidGearSteadyStateSynchronousResponseOnAShaft"
    ):
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3617,
        )

        return self.__parent__._cast(
            _3617.KlingelnbergCycloPalloidHypoidGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3619.KlingelnbergCycloPalloidSpiralBevelGearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3619,
        )

        return self.__parent__._cast(
            _3619.KlingelnbergCycloPalloidSpiralBevelGearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3620.KlingelnbergCycloPalloidSpiralBevelGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3620,
        )

        return self.__parent__._cast(
            _3620.KlingelnbergCycloPalloidSpiralBevelGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def mass_disc_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3621.MassDiscSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3621,
        )

        return self.__parent__._cast(
            _3621.MassDiscSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def measurement_component_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3622.MeasurementComponentSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3622,
        )

        return self.__parent__._cast(
            _3622.MeasurementComponentSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def microphone_array_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3623.MicrophoneArraySteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3623,
        )

        return self.__parent__._cast(
            _3623.MicrophoneArraySteadyStateSynchronousResponseOnAShaft
        )

    @property
    def microphone_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3624.MicrophoneSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3624,
        )

        return self.__parent__._cast(
            _3624.MicrophoneSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def mountable_component_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3625.MountableComponentSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3625,
        )

        return self.__parent__._cast(
            _3625.MountableComponentSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def oil_seal_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3626.OilSealSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3626,
        )

        return self.__parent__._cast(
            _3626.OilSealSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def part_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3627.PartSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3627,
        )

        return self.__parent__._cast(_3627.PartSteadyStateSynchronousResponseOnAShaft)

    @property
    def part_to_part_shear_coupling_half_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3629.PartToPartShearCouplingHalfSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3629,
        )

        return self.__parent__._cast(
            _3629.PartToPartShearCouplingHalfSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def part_to_part_shear_coupling_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3630.PartToPartShearCouplingSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3630,
        )

        return self.__parent__._cast(
            _3630.PartToPartShearCouplingSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def planetary_gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3632.PlanetaryGearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3632,
        )

        return self.__parent__._cast(
            _3632.PlanetaryGearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def planet_carrier_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3633.PlanetCarrierSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3633,
        )

        return self.__parent__._cast(
            _3633.PlanetCarrierSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def point_load_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3634.PointLoadSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3634,
        )

        return self.__parent__._cast(
            _3634.PointLoadSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def power_load_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3635.PowerLoadSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3635,
        )

        return self.__parent__._cast(
            _3635.PowerLoadSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def pulley_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3636.PulleySteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3636,
        )

        return self.__parent__._cast(_3636.PulleySteadyStateSynchronousResponseOnAShaft)

    @property
    def ring_pins_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3637.RingPinsSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3637,
        )

        return self.__parent__._cast(
            _3637.RingPinsSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def rolling_ring_assembly_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3639.RollingRingAssemblySteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3639,
        )

        return self.__parent__._cast(
            _3639.RollingRingAssemblySteadyStateSynchronousResponseOnAShaft
        )

    @property
    def rolling_ring_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3641.RollingRingSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3641,
        )

        return self.__parent__._cast(
            _3641.RollingRingSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def root_assembly_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3642.RootAssemblySteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3642,
        )

        return self.__parent__._cast(
            _3642.RootAssemblySteadyStateSynchronousResponseOnAShaft
        )

    @property
    def shaft_hub_connection_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3643.ShaftHubConnectionSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3643,
        )

        return self.__parent__._cast(
            _3643.ShaftHubConnectionSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def shaft_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3644.ShaftSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3644,
        )

        return self.__parent__._cast(_3644.ShaftSteadyStateSynchronousResponseOnAShaft)

    @property
    def specialised_assembly_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3646.SpecialisedAssemblySteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3646,
        )

        return self.__parent__._cast(
            _3646.SpecialisedAssemblySteadyStateSynchronousResponseOnAShaft
        )

    @property
    def spiral_bevel_gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3648.SpiralBevelGearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3648,
        )

        return self.__parent__._cast(
            _3648.SpiralBevelGearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def spiral_bevel_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3649.SpiralBevelGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3649,
        )

        return self.__parent__._cast(
            _3649.SpiralBevelGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def spring_damper_half_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3651.SpringDamperHalfSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3651,
        )

        return self.__parent__._cast(
            _3651.SpringDamperHalfSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def spring_damper_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3652.SpringDamperSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3652,
        )

        return self.__parent__._cast(
            _3652.SpringDamperSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_diff_gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3655.StraightBevelDiffGearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3655,
        )

        return self.__parent__._cast(
            _3655.StraightBevelDiffGearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_diff_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3656.StraightBevelDiffGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3656,
        )

        return self.__parent__._cast(
            _3656.StraightBevelDiffGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3658.StraightBevelGearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3658,
        )

        return self.__parent__._cast(
            _3658.StraightBevelGearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3659.StraightBevelGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3659,
        )

        return self.__parent__._cast(
            _3659.StraightBevelGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_planet_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3660.StraightBevelPlanetGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3660,
        )

        return self.__parent__._cast(
            _3660.StraightBevelPlanetGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_sun_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3661.StraightBevelSunGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3661,
        )

        return self.__parent__._cast(
            _3661.StraightBevelSunGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def synchroniser_half_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3662.SynchroniserHalfSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3662,
        )

        return self.__parent__._cast(
            _3662.SynchroniserHalfSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def synchroniser_part_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3663.SynchroniserPartSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3663,
        )

        return self.__parent__._cast(
            _3663.SynchroniserPartSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def synchroniser_sleeve_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3664.SynchroniserSleeveSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3664,
        )

        return self.__parent__._cast(
            _3664.SynchroniserSleeveSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def synchroniser_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3665.SynchroniserSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3665,
        )

        return self.__parent__._cast(
            _3665.SynchroniserSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def torque_converter_pump_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3667.TorqueConverterPumpSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3667,
        )

        return self.__parent__._cast(
            _3667.TorqueConverterPumpSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def torque_converter_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3668.TorqueConverterSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3668,
        )

        return self.__parent__._cast(
            _3668.TorqueConverterSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def torque_converter_turbine_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3669.TorqueConverterTurbineSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3669,
        )

        return self.__parent__._cast(
            _3669.TorqueConverterTurbineSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def unbalanced_mass_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3670.UnbalancedMassSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3670,
        )

        return self.__parent__._cast(
            _3670.UnbalancedMassSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def virtual_component_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3671.VirtualComponentSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3671,
        )

        return self.__parent__._cast(
            _3671.VirtualComponentSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def worm_gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3673.WormGearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3673,
        )

        return self.__parent__._cast(
            _3673.WormGearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def worm_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3674.WormGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3674,
        )

        return self.__parent__._cast(
            _3674.WormGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def zerol_bevel_gear_set_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3676.ZerolBevelGearSetSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3676,
        )

        return self.__parent__._cast(
            _3676.ZerolBevelGearSetSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def zerol_bevel_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3677.ZerolBevelGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3677,
        )

        return self.__parent__._cast(
            _3677.ZerolBevelGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def abstract_assembly_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3809.AbstractAssemblySteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3809,
        )

        return self.__parent__._cast(
            _3809.AbstractAssemblySteadyStateSynchronousResponseAtASpeed
        )

    @property
    def abstract_shaft_or_housing_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3810.AbstractShaftOrHousingSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3810,
        )

        return self.__parent__._cast(
            _3810.AbstractShaftOrHousingSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def abstract_shaft_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3811.AbstractShaftSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3811,
        )

        return self.__parent__._cast(
            _3811.AbstractShaftSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def agma_gleason_conical_gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3814.AGMAGleasonConicalGearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3814,
        )

        return self.__parent__._cast(
            _3814.AGMAGleasonConicalGearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def agma_gleason_conical_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3815.AGMAGleasonConicalGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3815,
        )

        return self.__parent__._cast(
            _3815.AGMAGleasonConicalGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def assembly_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3816.AssemblySteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3816,
        )

        return self.__parent__._cast(
            _3816.AssemblySteadyStateSynchronousResponseAtASpeed
        )

    @property
    def bearing_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3817.BearingSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3817,
        )

        return self.__parent__._cast(
            _3817.BearingSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def belt_drive_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3819.BeltDriveSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3819,
        )

        return self.__parent__._cast(
            _3819.BeltDriveSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def bevel_differential_gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3821.BevelDifferentialGearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3821,
        )

        return self.__parent__._cast(
            _3821.BevelDifferentialGearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def bevel_differential_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3822.BevelDifferentialGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3822,
        )

        return self.__parent__._cast(
            _3822.BevelDifferentialGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def bevel_differential_planet_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3823.BevelDifferentialPlanetGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3823,
        )

        return self.__parent__._cast(
            _3823.BevelDifferentialPlanetGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def bevel_differential_sun_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3824.BevelDifferentialSunGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3824,
        )

        return self.__parent__._cast(
            _3824.BevelDifferentialSunGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def bevel_gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3826.BevelGearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3826,
        )

        return self.__parent__._cast(
            _3826.BevelGearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def bevel_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3827.BevelGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3827,
        )

        return self.__parent__._cast(
            _3827.BevelGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def bolted_joint_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3828.BoltedJointSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3828,
        )

        return self.__parent__._cast(
            _3828.BoltedJointSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def bolt_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3829.BoltSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3829,
        )

        return self.__parent__._cast(_3829.BoltSteadyStateSynchronousResponseAtASpeed)

    @property
    def clutch_half_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3831.ClutchHalfSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3831,
        )

        return self.__parent__._cast(
            _3831.ClutchHalfSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def clutch_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3832.ClutchSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3832,
        )

        return self.__parent__._cast(_3832.ClutchSteadyStateSynchronousResponseAtASpeed)

    @property
    def component_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3834.ComponentSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3834,
        )

        return self.__parent__._cast(
            _3834.ComponentSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def concept_coupling_half_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3836.ConceptCouplingHalfSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3836,
        )

        return self.__parent__._cast(
            _3836.ConceptCouplingHalfSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def concept_coupling_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3837.ConceptCouplingSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3837,
        )

        return self.__parent__._cast(
            _3837.ConceptCouplingSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def concept_gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3839.ConceptGearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3839,
        )

        return self.__parent__._cast(
            _3839.ConceptGearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def concept_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3840.ConceptGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3840,
        )

        return self.__parent__._cast(
            _3840.ConceptGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def conical_gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3842.ConicalGearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3842,
        )

        return self.__parent__._cast(
            _3842.ConicalGearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def conical_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3843.ConicalGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3843,
        )

        return self.__parent__._cast(
            _3843.ConicalGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def connector_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3845.ConnectorSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3845,
        )

        return self.__parent__._cast(
            _3845.ConnectorSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def coupling_half_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3847.CouplingHalfSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3847,
        )

        return self.__parent__._cast(
            _3847.CouplingHalfSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def coupling_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3848.CouplingSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3848,
        )

        return self.__parent__._cast(
            _3848.CouplingSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def cvt_pulley_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3850.CVTPulleySteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3850,
        )

        return self.__parent__._cast(
            _3850.CVTPulleySteadyStateSynchronousResponseAtASpeed
        )

    @property
    def cvt_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3851.CVTSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3851,
        )

        return self.__parent__._cast(_3851.CVTSteadyStateSynchronousResponseAtASpeed)

    @property
    def cycloidal_assembly_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3852.CycloidalAssemblySteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3852,
        )

        return self.__parent__._cast(
            _3852.CycloidalAssemblySteadyStateSynchronousResponseAtASpeed
        )

    @property
    def cycloidal_disc_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3855.CycloidalDiscSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3855,
        )

        return self.__parent__._cast(
            _3855.CycloidalDiscSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def cylindrical_gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3857.CylindricalGearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3857,
        )

        return self.__parent__._cast(
            _3857.CylindricalGearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def cylindrical_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3858.CylindricalGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3858,
        )

        return self.__parent__._cast(
            _3858.CylindricalGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def cylindrical_planet_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3859.CylindricalPlanetGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3859,
        )

        return self.__parent__._cast(
            _3859.CylindricalPlanetGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def datum_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3860.DatumSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3860,
        )

        return self.__parent__._cast(_3860.DatumSteadyStateSynchronousResponseAtASpeed)

    @property
    def external_cad_model_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3861.ExternalCADModelSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3861,
        )

        return self.__parent__._cast(
            _3861.ExternalCADModelSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def face_gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3863.FaceGearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3863,
        )

        return self.__parent__._cast(
            _3863.FaceGearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def face_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3864.FaceGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3864,
        )

        return self.__parent__._cast(
            _3864.FaceGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def fe_part_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3865.FEPartSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3865,
        )

        return self.__parent__._cast(_3865.FEPartSteadyStateSynchronousResponseAtASpeed)

    @property
    def flexible_pin_assembly_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3866.FlexiblePinAssemblySteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3866,
        )

        return self.__parent__._cast(
            _3866.FlexiblePinAssemblySteadyStateSynchronousResponseAtASpeed
        )

    @property
    def gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3868.GearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3868,
        )

        return self.__parent__._cast(
            _3868.GearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3869.GearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3869,
        )

        return self.__parent__._cast(_3869.GearSteadyStateSynchronousResponseAtASpeed)

    @property
    def guide_dxf_model_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3870.GuideDxfModelSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3870,
        )

        return self.__parent__._cast(
            _3870.GuideDxfModelSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def hypoid_gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3872.HypoidGearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3872,
        )

        return self.__parent__._cast(
            _3872.HypoidGearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def hypoid_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3873.HypoidGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3873,
        )

        return self.__parent__._cast(
            _3873.HypoidGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3876.KlingelnbergCycloPalloidConicalGearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3876,
        )

        return self.__parent__._cast(
            _3876.KlingelnbergCycloPalloidConicalGearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3877.KlingelnbergCycloPalloidConicalGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3877,
        )

        return self.__parent__._cast(
            _3877.KlingelnbergCycloPalloidConicalGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3879.KlingelnbergCycloPalloidHypoidGearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3879,
        )

        return self.__parent__._cast(
            _3879.KlingelnbergCycloPalloidHypoidGearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> (
        "_3880.KlingelnbergCycloPalloidHypoidGearSteadyStateSynchronousResponseAtASpeed"
    ):
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3880,
        )

        return self.__parent__._cast(
            _3880.KlingelnbergCycloPalloidHypoidGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3882.KlingelnbergCycloPalloidSpiralBevelGearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3882,
        )

        return self.__parent__._cast(
            _3882.KlingelnbergCycloPalloidSpiralBevelGearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3883.KlingelnbergCycloPalloidSpiralBevelGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3883,
        )

        return self.__parent__._cast(
            _3883.KlingelnbergCycloPalloidSpiralBevelGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def mass_disc_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3884.MassDiscSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3884,
        )

        return self.__parent__._cast(
            _3884.MassDiscSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def measurement_component_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3885.MeasurementComponentSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3885,
        )

        return self.__parent__._cast(
            _3885.MeasurementComponentSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def microphone_array_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3886.MicrophoneArraySteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3886,
        )

        return self.__parent__._cast(
            _3886.MicrophoneArraySteadyStateSynchronousResponseAtASpeed
        )

    @property
    def microphone_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3887.MicrophoneSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3887,
        )

        return self.__parent__._cast(
            _3887.MicrophoneSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def mountable_component_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3888.MountableComponentSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3888,
        )

        return self.__parent__._cast(
            _3888.MountableComponentSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def oil_seal_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3889.OilSealSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3889,
        )

        return self.__parent__._cast(
            _3889.OilSealSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def part_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3890.PartSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3890,
        )

        return self.__parent__._cast(_3890.PartSteadyStateSynchronousResponseAtASpeed)

    @property
    def part_to_part_shear_coupling_half_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3892.PartToPartShearCouplingHalfSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3892,
        )

        return self.__parent__._cast(
            _3892.PartToPartShearCouplingHalfSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def part_to_part_shear_coupling_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3893.PartToPartShearCouplingSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3893,
        )

        return self.__parent__._cast(
            _3893.PartToPartShearCouplingSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def planetary_gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3895.PlanetaryGearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3895,
        )

        return self.__parent__._cast(
            _3895.PlanetaryGearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def planet_carrier_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3896.PlanetCarrierSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3896,
        )

        return self.__parent__._cast(
            _3896.PlanetCarrierSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def point_load_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3897.PointLoadSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3897,
        )

        return self.__parent__._cast(
            _3897.PointLoadSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def power_load_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3898.PowerLoadSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3898,
        )

        return self.__parent__._cast(
            _3898.PowerLoadSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def pulley_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3899.PulleySteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3899,
        )

        return self.__parent__._cast(_3899.PulleySteadyStateSynchronousResponseAtASpeed)

    @property
    def ring_pins_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3900.RingPinsSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3900,
        )

        return self.__parent__._cast(
            _3900.RingPinsSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def rolling_ring_assembly_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3902.RollingRingAssemblySteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3902,
        )

        return self.__parent__._cast(
            _3902.RollingRingAssemblySteadyStateSynchronousResponseAtASpeed
        )

    @property
    def rolling_ring_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3904.RollingRingSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3904,
        )

        return self.__parent__._cast(
            _3904.RollingRingSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def root_assembly_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3905.RootAssemblySteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3905,
        )

        return self.__parent__._cast(
            _3905.RootAssemblySteadyStateSynchronousResponseAtASpeed
        )

    @property
    def shaft_hub_connection_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3906.ShaftHubConnectionSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3906,
        )

        return self.__parent__._cast(
            _3906.ShaftHubConnectionSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def shaft_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3907.ShaftSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3907,
        )

        return self.__parent__._cast(_3907.ShaftSteadyStateSynchronousResponseAtASpeed)

    @property
    def specialised_assembly_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3909.SpecialisedAssemblySteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3909,
        )

        return self.__parent__._cast(
            _3909.SpecialisedAssemblySteadyStateSynchronousResponseAtASpeed
        )

    @property
    def spiral_bevel_gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3911.SpiralBevelGearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3911,
        )

        return self.__parent__._cast(
            _3911.SpiralBevelGearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def spiral_bevel_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3912.SpiralBevelGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3912,
        )

        return self.__parent__._cast(
            _3912.SpiralBevelGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def spring_damper_half_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3914.SpringDamperHalfSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3914,
        )

        return self.__parent__._cast(
            _3914.SpringDamperHalfSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def spring_damper_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3915.SpringDamperSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3915,
        )

        return self.__parent__._cast(
            _3915.SpringDamperSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def straight_bevel_diff_gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3918.StraightBevelDiffGearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3918,
        )

        return self.__parent__._cast(
            _3918.StraightBevelDiffGearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def straight_bevel_diff_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3919.StraightBevelDiffGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3919,
        )

        return self.__parent__._cast(
            _3919.StraightBevelDiffGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def straight_bevel_gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3921.StraightBevelGearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3921,
        )

        return self.__parent__._cast(
            _3921.StraightBevelGearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def straight_bevel_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3922.StraightBevelGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3922,
        )

        return self.__parent__._cast(
            _3922.StraightBevelGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def straight_bevel_planet_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3923.StraightBevelPlanetGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3923,
        )

        return self.__parent__._cast(
            _3923.StraightBevelPlanetGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def straight_bevel_sun_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3924.StraightBevelSunGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3924,
        )

        return self.__parent__._cast(
            _3924.StraightBevelSunGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def synchroniser_half_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3925.SynchroniserHalfSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3925,
        )

        return self.__parent__._cast(
            _3925.SynchroniserHalfSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def synchroniser_part_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3926.SynchroniserPartSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3926,
        )

        return self.__parent__._cast(
            _3926.SynchroniserPartSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def synchroniser_sleeve_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3927.SynchroniserSleeveSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3927,
        )

        return self.__parent__._cast(
            _3927.SynchroniserSleeveSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def synchroniser_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3928.SynchroniserSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3928,
        )

        return self.__parent__._cast(
            _3928.SynchroniserSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def torque_converter_pump_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3930.TorqueConverterPumpSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3930,
        )

        return self.__parent__._cast(
            _3930.TorqueConverterPumpSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def torque_converter_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3931.TorqueConverterSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3931,
        )

        return self.__parent__._cast(
            _3931.TorqueConverterSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def torque_converter_turbine_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3932.TorqueConverterTurbineSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3932,
        )

        return self.__parent__._cast(
            _3932.TorqueConverterTurbineSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def unbalanced_mass_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3933.UnbalancedMassSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3933,
        )

        return self.__parent__._cast(
            _3933.UnbalancedMassSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def virtual_component_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3934.VirtualComponentSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3934,
        )

        return self.__parent__._cast(
            _3934.VirtualComponentSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def worm_gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3936.WormGearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3936,
        )

        return self.__parent__._cast(
            _3936.WormGearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def worm_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3937.WormGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3937,
        )

        return self.__parent__._cast(
            _3937.WormGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def zerol_bevel_gear_set_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3939.ZerolBevelGearSetSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3939,
        )

        return self.__parent__._cast(
            _3939.ZerolBevelGearSetSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def zerol_bevel_gear_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3940.ZerolBevelGearSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3940,
        )

        return self.__parent__._cast(
            _3940.ZerolBevelGearSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def abstract_assembly_stability_analysis(
        self: "CastSelf",
    ) -> "_4072.AbstractAssemblyStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4072,
        )

        return self.__parent__._cast(_4072.AbstractAssemblyStabilityAnalysis)

    @property
    def abstract_shaft_or_housing_stability_analysis(
        self: "CastSelf",
    ) -> "_4073.AbstractShaftOrHousingStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4073,
        )

        return self.__parent__._cast(_4073.AbstractShaftOrHousingStabilityAnalysis)

    @property
    def abstract_shaft_stability_analysis(
        self: "CastSelf",
    ) -> "_4074.AbstractShaftStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4074,
        )

        return self.__parent__._cast(_4074.AbstractShaftStabilityAnalysis)

    @property
    def agma_gleason_conical_gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4077.AGMAGleasonConicalGearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4077,
        )

        return self.__parent__._cast(_4077.AGMAGleasonConicalGearSetStabilityAnalysis)

    @property
    def agma_gleason_conical_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4078.AGMAGleasonConicalGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4078,
        )

        return self.__parent__._cast(_4078.AGMAGleasonConicalGearStabilityAnalysis)

    @property
    def assembly_stability_analysis(
        self: "CastSelf",
    ) -> "_4079.AssemblyStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4079,
        )

        return self.__parent__._cast(_4079.AssemblyStabilityAnalysis)

    @property
    def bearing_stability_analysis(
        self: "CastSelf",
    ) -> "_4080.BearingStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4080,
        )

        return self.__parent__._cast(_4080.BearingStabilityAnalysis)

    @property
    def belt_drive_stability_analysis(
        self: "CastSelf",
    ) -> "_4082.BeltDriveStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4082,
        )

        return self.__parent__._cast(_4082.BeltDriveStabilityAnalysis)

    @property
    def bevel_differential_gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4084.BevelDifferentialGearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4084,
        )

        return self.__parent__._cast(_4084.BevelDifferentialGearSetStabilityAnalysis)

    @property
    def bevel_differential_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4085.BevelDifferentialGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4085,
        )

        return self.__parent__._cast(_4085.BevelDifferentialGearStabilityAnalysis)

    @property
    def bevel_differential_planet_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4086.BevelDifferentialPlanetGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4086,
        )

        return self.__parent__._cast(_4086.BevelDifferentialPlanetGearStabilityAnalysis)

    @property
    def bevel_differential_sun_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4087.BevelDifferentialSunGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4087,
        )

        return self.__parent__._cast(_4087.BevelDifferentialSunGearStabilityAnalysis)

    @property
    def bevel_gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4089.BevelGearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4089,
        )

        return self.__parent__._cast(_4089.BevelGearSetStabilityAnalysis)

    @property
    def bevel_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4090.BevelGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4090,
        )

        return self.__parent__._cast(_4090.BevelGearStabilityAnalysis)

    @property
    def bolted_joint_stability_analysis(
        self: "CastSelf",
    ) -> "_4091.BoltedJointStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4091,
        )

        return self.__parent__._cast(_4091.BoltedJointStabilityAnalysis)

    @property
    def bolt_stability_analysis(self: "CastSelf") -> "_4092.BoltStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4092,
        )

        return self.__parent__._cast(_4092.BoltStabilityAnalysis)

    @property
    def clutch_half_stability_analysis(
        self: "CastSelf",
    ) -> "_4094.ClutchHalfStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4094,
        )

        return self.__parent__._cast(_4094.ClutchHalfStabilityAnalysis)

    @property
    def clutch_stability_analysis(self: "CastSelf") -> "_4095.ClutchStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4095,
        )

        return self.__parent__._cast(_4095.ClutchStabilityAnalysis)

    @property
    def component_stability_analysis(
        self: "CastSelf",
    ) -> "_4097.ComponentStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4097,
        )

        return self.__parent__._cast(_4097.ComponentStabilityAnalysis)

    @property
    def concept_coupling_half_stability_analysis(
        self: "CastSelf",
    ) -> "_4099.ConceptCouplingHalfStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4099,
        )

        return self.__parent__._cast(_4099.ConceptCouplingHalfStabilityAnalysis)

    @property
    def concept_coupling_stability_analysis(
        self: "CastSelf",
    ) -> "_4100.ConceptCouplingStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4100,
        )

        return self.__parent__._cast(_4100.ConceptCouplingStabilityAnalysis)

    @property
    def concept_gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4102.ConceptGearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4102,
        )

        return self.__parent__._cast(_4102.ConceptGearSetStabilityAnalysis)

    @property
    def concept_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4103.ConceptGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4103,
        )

        return self.__parent__._cast(_4103.ConceptGearStabilityAnalysis)

    @property
    def conical_gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4105.ConicalGearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4105,
        )

        return self.__parent__._cast(_4105.ConicalGearSetStabilityAnalysis)

    @property
    def conical_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4106.ConicalGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4106,
        )

        return self.__parent__._cast(_4106.ConicalGearStabilityAnalysis)

    @property
    def connector_stability_analysis(
        self: "CastSelf",
    ) -> "_4108.ConnectorStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4108,
        )

        return self.__parent__._cast(_4108.ConnectorStabilityAnalysis)

    @property
    def coupling_half_stability_analysis(
        self: "CastSelf",
    ) -> "_4110.CouplingHalfStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4110,
        )

        return self.__parent__._cast(_4110.CouplingHalfStabilityAnalysis)

    @property
    def coupling_stability_analysis(
        self: "CastSelf",
    ) -> "_4111.CouplingStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4111,
        )

        return self.__parent__._cast(_4111.CouplingStabilityAnalysis)

    @property
    def cvt_pulley_stability_analysis(
        self: "CastSelf",
    ) -> "_4114.CVTPulleyStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4114,
        )

        return self.__parent__._cast(_4114.CVTPulleyStabilityAnalysis)

    @property
    def cvt_stability_analysis(self: "CastSelf") -> "_4115.CVTStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4115,
        )

        return self.__parent__._cast(_4115.CVTStabilityAnalysis)

    @property
    def cycloidal_assembly_stability_analysis(
        self: "CastSelf",
    ) -> "_4116.CycloidalAssemblyStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4116,
        )

        return self.__parent__._cast(_4116.CycloidalAssemblyStabilityAnalysis)

    @property
    def cycloidal_disc_stability_analysis(
        self: "CastSelf",
    ) -> "_4119.CycloidalDiscStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4119,
        )

        return self.__parent__._cast(_4119.CycloidalDiscStabilityAnalysis)

    @property
    def cylindrical_gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4121.CylindricalGearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4121,
        )

        return self.__parent__._cast(_4121.CylindricalGearSetStabilityAnalysis)

    @property
    def cylindrical_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4122.CylindricalGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4122,
        )

        return self.__parent__._cast(_4122.CylindricalGearStabilityAnalysis)

    @property
    def cylindrical_planet_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4123.CylindricalPlanetGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4123,
        )

        return self.__parent__._cast(_4123.CylindricalPlanetGearStabilityAnalysis)

    @property
    def datum_stability_analysis(self: "CastSelf") -> "_4124.DatumStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4124,
        )

        return self.__parent__._cast(_4124.DatumStabilityAnalysis)

    @property
    def external_cad_model_stability_analysis(
        self: "CastSelf",
    ) -> "_4126.ExternalCADModelStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4126,
        )

        return self.__parent__._cast(_4126.ExternalCADModelStabilityAnalysis)

    @property
    def face_gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4128.FaceGearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4128,
        )

        return self.__parent__._cast(_4128.FaceGearSetStabilityAnalysis)

    @property
    def face_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4129.FaceGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4129,
        )

        return self.__parent__._cast(_4129.FaceGearStabilityAnalysis)

    @property
    def fe_part_stability_analysis(self: "CastSelf") -> "_4130.FEPartStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4130,
        )

        return self.__parent__._cast(_4130.FEPartStabilityAnalysis)

    @property
    def flexible_pin_assembly_stability_analysis(
        self: "CastSelf",
    ) -> "_4131.FlexiblePinAssemblyStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4131,
        )

        return self.__parent__._cast(_4131.FlexiblePinAssemblyStabilityAnalysis)

    @property
    def gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4133.GearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4133,
        )

        return self.__parent__._cast(_4133.GearSetStabilityAnalysis)

    @property
    def gear_stability_analysis(self: "CastSelf") -> "_4134.GearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4134,
        )

        return self.__parent__._cast(_4134.GearStabilityAnalysis)

    @property
    def guide_dxf_model_stability_analysis(
        self: "CastSelf",
    ) -> "_4135.GuideDxfModelStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4135,
        )

        return self.__parent__._cast(_4135.GuideDxfModelStabilityAnalysis)

    @property
    def hypoid_gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4137.HypoidGearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4137,
        )

        return self.__parent__._cast(_4137.HypoidGearSetStabilityAnalysis)

    @property
    def hypoid_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4138.HypoidGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4138,
        )

        return self.__parent__._cast(_4138.HypoidGearStabilityAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4141.KlingelnbergCycloPalloidConicalGearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4141,
        )

        return self.__parent__._cast(
            _4141.KlingelnbergCycloPalloidConicalGearSetStabilityAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4142.KlingelnbergCycloPalloidConicalGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4142,
        )

        return self.__parent__._cast(
            _4142.KlingelnbergCycloPalloidConicalGearStabilityAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4144.KlingelnbergCycloPalloidHypoidGearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4144,
        )

        return self.__parent__._cast(
            _4144.KlingelnbergCycloPalloidHypoidGearSetStabilityAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4145.KlingelnbergCycloPalloidHypoidGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4145,
        )

        return self.__parent__._cast(
            _4145.KlingelnbergCycloPalloidHypoidGearStabilityAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4147.KlingelnbergCycloPalloidSpiralBevelGearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4147,
        )

        return self.__parent__._cast(
            _4147.KlingelnbergCycloPalloidSpiralBevelGearSetStabilityAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4148.KlingelnbergCycloPalloidSpiralBevelGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4148,
        )

        return self.__parent__._cast(
            _4148.KlingelnbergCycloPalloidSpiralBevelGearStabilityAnalysis
        )

    @property
    def mass_disc_stability_analysis(
        self: "CastSelf",
    ) -> "_4149.MassDiscStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4149,
        )

        return self.__parent__._cast(_4149.MassDiscStabilityAnalysis)

    @property
    def measurement_component_stability_analysis(
        self: "CastSelf",
    ) -> "_4150.MeasurementComponentStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4150,
        )

        return self.__parent__._cast(_4150.MeasurementComponentStabilityAnalysis)

    @property
    def microphone_array_stability_analysis(
        self: "CastSelf",
    ) -> "_4151.MicrophoneArrayStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4151,
        )

        return self.__parent__._cast(_4151.MicrophoneArrayStabilityAnalysis)

    @property
    def microphone_stability_analysis(
        self: "CastSelf",
    ) -> "_4152.MicrophoneStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4152,
        )

        return self.__parent__._cast(_4152.MicrophoneStabilityAnalysis)

    @property
    def mountable_component_stability_analysis(
        self: "CastSelf",
    ) -> "_4153.MountableComponentStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4153,
        )

        return self.__parent__._cast(_4153.MountableComponentStabilityAnalysis)

    @property
    def oil_seal_stability_analysis(
        self: "CastSelf",
    ) -> "_4154.OilSealStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4154,
        )

        return self.__parent__._cast(_4154.OilSealStabilityAnalysis)

    @property
    def part_stability_analysis(self: "CastSelf") -> "_4155.PartStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4155,
        )

        return self.__parent__._cast(_4155.PartStabilityAnalysis)

    @property
    def part_to_part_shear_coupling_half_stability_analysis(
        self: "CastSelf",
    ) -> "_4157.PartToPartShearCouplingHalfStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4157,
        )

        return self.__parent__._cast(_4157.PartToPartShearCouplingHalfStabilityAnalysis)

    @property
    def part_to_part_shear_coupling_stability_analysis(
        self: "CastSelf",
    ) -> "_4158.PartToPartShearCouplingStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4158,
        )

        return self.__parent__._cast(_4158.PartToPartShearCouplingStabilityAnalysis)

    @property
    def planetary_gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4160.PlanetaryGearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4160,
        )

        return self.__parent__._cast(_4160.PlanetaryGearSetStabilityAnalysis)

    @property
    def planet_carrier_stability_analysis(
        self: "CastSelf",
    ) -> "_4161.PlanetCarrierStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4161,
        )

        return self.__parent__._cast(_4161.PlanetCarrierStabilityAnalysis)

    @property
    def point_load_stability_analysis(
        self: "CastSelf",
    ) -> "_4162.PointLoadStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4162,
        )

        return self.__parent__._cast(_4162.PointLoadStabilityAnalysis)

    @property
    def power_load_stability_analysis(
        self: "CastSelf",
    ) -> "_4163.PowerLoadStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4163,
        )

        return self.__parent__._cast(_4163.PowerLoadStabilityAnalysis)

    @property
    def pulley_stability_analysis(self: "CastSelf") -> "_4164.PulleyStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4164,
        )

        return self.__parent__._cast(_4164.PulleyStabilityAnalysis)

    @property
    def ring_pins_stability_analysis(
        self: "CastSelf",
    ) -> "_4165.RingPinsStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4165,
        )

        return self.__parent__._cast(_4165.RingPinsStabilityAnalysis)

    @property
    def rolling_ring_assembly_stability_analysis(
        self: "CastSelf",
    ) -> "_4167.RollingRingAssemblyStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4167,
        )

        return self.__parent__._cast(_4167.RollingRingAssemblyStabilityAnalysis)

    @property
    def rolling_ring_stability_analysis(
        self: "CastSelf",
    ) -> "_4169.RollingRingStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4169,
        )

        return self.__parent__._cast(_4169.RollingRingStabilityAnalysis)

    @property
    def root_assembly_stability_analysis(
        self: "CastSelf",
    ) -> "_4170.RootAssemblyStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4170,
        )

        return self.__parent__._cast(_4170.RootAssemblyStabilityAnalysis)

    @property
    def shaft_hub_connection_stability_analysis(
        self: "CastSelf",
    ) -> "_4171.ShaftHubConnectionStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4171,
        )

        return self.__parent__._cast(_4171.ShaftHubConnectionStabilityAnalysis)

    @property
    def shaft_stability_analysis(self: "CastSelf") -> "_4172.ShaftStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4172,
        )

        return self.__parent__._cast(_4172.ShaftStabilityAnalysis)

    @property
    def specialised_assembly_stability_analysis(
        self: "CastSelf",
    ) -> "_4174.SpecialisedAssemblyStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4174,
        )

        return self.__parent__._cast(_4174.SpecialisedAssemblyStabilityAnalysis)

    @property
    def spiral_bevel_gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4176.SpiralBevelGearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4176,
        )

        return self.__parent__._cast(_4176.SpiralBevelGearSetStabilityAnalysis)

    @property
    def spiral_bevel_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4177.SpiralBevelGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4177,
        )

        return self.__parent__._cast(_4177.SpiralBevelGearStabilityAnalysis)

    @property
    def spring_damper_half_stability_analysis(
        self: "CastSelf",
    ) -> "_4179.SpringDamperHalfStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4179,
        )

        return self.__parent__._cast(_4179.SpringDamperHalfStabilityAnalysis)

    @property
    def spring_damper_stability_analysis(
        self: "CastSelf",
    ) -> "_4180.SpringDamperStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4180,
        )

        return self.__parent__._cast(_4180.SpringDamperStabilityAnalysis)

    @property
    def straight_bevel_diff_gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4185.StraightBevelDiffGearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4185,
        )

        return self.__parent__._cast(_4185.StraightBevelDiffGearSetStabilityAnalysis)

    @property
    def straight_bevel_diff_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4186.StraightBevelDiffGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4186,
        )

        return self.__parent__._cast(_4186.StraightBevelDiffGearStabilityAnalysis)

    @property
    def straight_bevel_gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4188.StraightBevelGearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4188,
        )

        return self.__parent__._cast(_4188.StraightBevelGearSetStabilityAnalysis)

    @property
    def straight_bevel_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4189.StraightBevelGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4189,
        )

        return self.__parent__._cast(_4189.StraightBevelGearStabilityAnalysis)

    @property
    def straight_bevel_planet_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4190.StraightBevelPlanetGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4190,
        )

        return self.__parent__._cast(_4190.StraightBevelPlanetGearStabilityAnalysis)

    @property
    def straight_bevel_sun_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4191.StraightBevelSunGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4191,
        )

        return self.__parent__._cast(_4191.StraightBevelSunGearStabilityAnalysis)

    @property
    def synchroniser_half_stability_analysis(
        self: "CastSelf",
    ) -> "_4192.SynchroniserHalfStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4192,
        )

        return self.__parent__._cast(_4192.SynchroniserHalfStabilityAnalysis)

    @property
    def synchroniser_part_stability_analysis(
        self: "CastSelf",
    ) -> "_4193.SynchroniserPartStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4193,
        )

        return self.__parent__._cast(_4193.SynchroniserPartStabilityAnalysis)

    @property
    def synchroniser_sleeve_stability_analysis(
        self: "CastSelf",
    ) -> "_4194.SynchroniserSleeveStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4194,
        )

        return self.__parent__._cast(_4194.SynchroniserSleeveStabilityAnalysis)

    @property
    def synchroniser_stability_analysis(
        self: "CastSelf",
    ) -> "_4195.SynchroniserStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4195,
        )

        return self.__parent__._cast(_4195.SynchroniserStabilityAnalysis)

    @property
    def torque_converter_pump_stability_analysis(
        self: "CastSelf",
    ) -> "_4197.TorqueConverterPumpStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4197,
        )

        return self.__parent__._cast(_4197.TorqueConverterPumpStabilityAnalysis)

    @property
    def torque_converter_stability_analysis(
        self: "CastSelf",
    ) -> "_4198.TorqueConverterStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4198,
        )

        return self.__parent__._cast(_4198.TorqueConverterStabilityAnalysis)

    @property
    def torque_converter_turbine_stability_analysis(
        self: "CastSelf",
    ) -> "_4199.TorqueConverterTurbineStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4199,
        )

        return self.__parent__._cast(_4199.TorqueConverterTurbineStabilityAnalysis)

    @property
    def unbalanced_mass_stability_analysis(
        self: "CastSelf",
    ) -> "_4200.UnbalancedMassStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4200,
        )

        return self.__parent__._cast(_4200.UnbalancedMassStabilityAnalysis)

    @property
    def virtual_component_stability_analysis(
        self: "CastSelf",
    ) -> "_4201.VirtualComponentStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4201,
        )

        return self.__parent__._cast(_4201.VirtualComponentStabilityAnalysis)

    @property
    def worm_gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4203.WormGearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4203,
        )

        return self.__parent__._cast(_4203.WormGearSetStabilityAnalysis)

    @property
    def worm_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4204.WormGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4204,
        )

        return self.__parent__._cast(_4204.WormGearStabilityAnalysis)

    @property
    def zerol_bevel_gear_set_stability_analysis(
        self: "CastSelf",
    ) -> "_4206.ZerolBevelGearSetStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4206,
        )

        return self.__parent__._cast(_4206.ZerolBevelGearSetStabilityAnalysis)

    @property
    def zerol_bevel_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4207.ZerolBevelGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4207,
        )

        return self.__parent__._cast(_4207.ZerolBevelGearStabilityAnalysis)

    @property
    def abstract_assembly_power_flow(
        self: "CastSelf",
    ) -> "_4345.AbstractAssemblyPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4345

        return self.__parent__._cast(_4345.AbstractAssemblyPowerFlow)

    @property
    def abstract_shaft_or_housing_power_flow(
        self: "CastSelf",
    ) -> "_4346.AbstractShaftOrHousingPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4346

        return self.__parent__._cast(_4346.AbstractShaftOrHousingPowerFlow)

    @property
    def abstract_shaft_power_flow(self: "CastSelf") -> "_4347.AbstractShaftPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4347

        return self.__parent__._cast(_4347.AbstractShaftPowerFlow)

    @property
    def agma_gleason_conical_gear_power_flow(
        self: "CastSelf",
    ) -> "_4350.AGMAGleasonConicalGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4350

        return self.__parent__._cast(_4350.AGMAGleasonConicalGearPowerFlow)

    @property
    def agma_gleason_conical_gear_set_power_flow(
        self: "CastSelf",
    ) -> "_4351.AGMAGleasonConicalGearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4351

        return self.__parent__._cast(_4351.AGMAGleasonConicalGearSetPowerFlow)

    @property
    def assembly_power_flow(self: "CastSelf") -> "_4352.AssemblyPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4352

        return self.__parent__._cast(_4352.AssemblyPowerFlow)

    @property
    def bearing_power_flow(self: "CastSelf") -> "_4353.BearingPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4353

        return self.__parent__._cast(_4353.BearingPowerFlow)

    @property
    def belt_drive_power_flow(self: "CastSelf") -> "_4355.BeltDrivePowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4355

        return self.__parent__._cast(_4355.BeltDrivePowerFlow)

    @property
    def bevel_differential_gear_power_flow(
        self: "CastSelf",
    ) -> "_4357.BevelDifferentialGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4357

        return self.__parent__._cast(_4357.BevelDifferentialGearPowerFlow)

    @property
    def bevel_differential_gear_set_power_flow(
        self: "CastSelf",
    ) -> "_4358.BevelDifferentialGearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4358

        return self.__parent__._cast(_4358.BevelDifferentialGearSetPowerFlow)

    @property
    def bevel_differential_planet_gear_power_flow(
        self: "CastSelf",
    ) -> "_4359.BevelDifferentialPlanetGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4359

        return self.__parent__._cast(_4359.BevelDifferentialPlanetGearPowerFlow)

    @property
    def bevel_differential_sun_gear_power_flow(
        self: "CastSelf",
    ) -> "_4360.BevelDifferentialSunGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4360

        return self.__parent__._cast(_4360.BevelDifferentialSunGearPowerFlow)

    @property
    def bevel_gear_power_flow(self: "CastSelf") -> "_4362.BevelGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4362

        return self.__parent__._cast(_4362.BevelGearPowerFlow)

    @property
    def bevel_gear_set_power_flow(self: "CastSelf") -> "_4363.BevelGearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4363

        return self.__parent__._cast(_4363.BevelGearSetPowerFlow)

    @property
    def bolted_joint_power_flow(self: "CastSelf") -> "_4364.BoltedJointPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4364

        return self.__parent__._cast(_4364.BoltedJointPowerFlow)

    @property
    def bolt_power_flow(self: "CastSelf") -> "_4365.BoltPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4365

        return self.__parent__._cast(_4365.BoltPowerFlow)

    @property
    def clutch_half_power_flow(self: "CastSelf") -> "_4367.ClutchHalfPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4367

        return self.__parent__._cast(_4367.ClutchHalfPowerFlow)

    @property
    def clutch_power_flow(self: "CastSelf") -> "_4368.ClutchPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4368

        return self.__parent__._cast(_4368.ClutchPowerFlow)

    @property
    def component_power_flow(self: "CastSelf") -> "_4370.ComponentPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4370

        return self.__parent__._cast(_4370.ComponentPowerFlow)

    @property
    def concept_coupling_half_power_flow(
        self: "CastSelf",
    ) -> "_4372.ConceptCouplingHalfPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4372

        return self.__parent__._cast(_4372.ConceptCouplingHalfPowerFlow)

    @property
    def concept_coupling_power_flow(
        self: "CastSelf",
    ) -> "_4373.ConceptCouplingPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4373

        return self.__parent__._cast(_4373.ConceptCouplingPowerFlow)

    @property
    def concept_gear_power_flow(self: "CastSelf") -> "_4375.ConceptGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4375

        return self.__parent__._cast(_4375.ConceptGearPowerFlow)

    @property
    def concept_gear_set_power_flow(
        self: "CastSelf",
    ) -> "_4376.ConceptGearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4376

        return self.__parent__._cast(_4376.ConceptGearSetPowerFlow)

    @property
    def conical_gear_power_flow(self: "CastSelf") -> "_4378.ConicalGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4378

        return self.__parent__._cast(_4378.ConicalGearPowerFlow)

    @property
    def conical_gear_set_power_flow(
        self: "CastSelf",
    ) -> "_4379.ConicalGearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4379

        return self.__parent__._cast(_4379.ConicalGearSetPowerFlow)

    @property
    def connector_power_flow(self: "CastSelf") -> "_4381.ConnectorPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4381

        return self.__parent__._cast(_4381.ConnectorPowerFlow)

    @property
    def coupling_half_power_flow(self: "CastSelf") -> "_4383.CouplingHalfPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4383

        return self.__parent__._cast(_4383.CouplingHalfPowerFlow)

    @property
    def coupling_power_flow(self: "CastSelf") -> "_4384.CouplingPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4384

        return self.__parent__._cast(_4384.CouplingPowerFlow)

    @property
    def cvt_power_flow(self: "CastSelf") -> "_4386.CVTPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4386

        return self.__parent__._cast(_4386.CVTPowerFlow)

    @property
    def cvt_pulley_power_flow(self: "CastSelf") -> "_4387.CVTPulleyPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4387

        return self.__parent__._cast(_4387.CVTPulleyPowerFlow)

    @property
    def cycloidal_assembly_power_flow(
        self: "CastSelf",
    ) -> "_4388.CycloidalAssemblyPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4388

        return self.__parent__._cast(_4388.CycloidalAssemblyPowerFlow)

    @property
    def cycloidal_disc_power_flow(self: "CastSelf") -> "_4391.CycloidalDiscPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4391

        return self.__parent__._cast(_4391.CycloidalDiscPowerFlow)

    @property
    def cylindrical_gear_power_flow(
        self: "CastSelf",
    ) -> "_4394.CylindricalGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4394

        return self.__parent__._cast(_4394.CylindricalGearPowerFlow)

    @property
    def cylindrical_gear_set_power_flow(
        self: "CastSelf",
    ) -> "_4395.CylindricalGearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4395

        return self.__parent__._cast(_4395.CylindricalGearSetPowerFlow)

    @property
    def cylindrical_planet_gear_power_flow(
        self: "CastSelf",
    ) -> "_4396.CylindricalPlanetGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4396

        return self.__parent__._cast(_4396.CylindricalPlanetGearPowerFlow)

    @property
    def datum_power_flow(self: "CastSelf") -> "_4397.DatumPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4397

        return self.__parent__._cast(_4397.DatumPowerFlow)

    @property
    def external_cad_model_power_flow(
        self: "CastSelf",
    ) -> "_4398.ExternalCADModelPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4398

        return self.__parent__._cast(_4398.ExternalCADModelPowerFlow)

    @property
    def face_gear_power_flow(self: "CastSelf") -> "_4400.FaceGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4400

        return self.__parent__._cast(_4400.FaceGearPowerFlow)

    @property
    def face_gear_set_power_flow(self: "CastSelf") -> "_4401.FaceGearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4401

        return self.__parent__._cast(_4401.FaceGearSetPowerFlow)

    @property
    def fe_part_power_flow(self: "CastSelf") -> "_4404.FEPartPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4404

        return self.__parent__._cast(_4404.FEPartPowerFlow)

    @property
    def flexible_pin_assembly_power_flow(
        self: "CastSelf",
    ) -> "_4405.FlexiblePinAssemblyPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4405

        return self.__parent__._cast(_4405.FlexiblePinAssemblyPowerFlow)

    @property
    def gear_power_flow(self: "CastSelf") -> "_4407.GearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4407

        return self.__parent__._cast(_4407.GearPowerFlow)

    @property
    def gear_set_power_flow(self: "CastSelf") -> "_4408.GearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4408

        return self.__parent__._cast(_4408.GearSetPowerFlow)

    @property
    def guide_dxf_model_power_flow(self: "CastSelf") -> "_4409.GuideDxfModelPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4409

        return self.__parent__._cast(_4409.GuideDxfModelPowerFlow)

    @property
    def hypoid_gear_power_flow(self: "CastSelf") -> "_4411.HypoidGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4411

        return self.__parent__._cast(_4411.HypoidGearPowerFlow)

    @property
    def hypoid_gear_set_power_flow(self: "CastSelf") -> "_4412.HypoidGearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4412

        return self.__parent__._cast(_4412.HypoidGearSetPowerFlow)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_power_flow(
        self: "CastSelf",
    ) -> "_4415.KlingelnbergCycloPalloidConicalGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4415

        return self.__parent__._cast(_4415.KlingelnbergCycloPalloidConicalGearPowerFlow)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_power_flow(
        self: "CastSelf",
    ) -> "_4416.KlingelnbergCycloPalloidConicalGearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4416

        return self.__parent__._cast(
            _4416.KlingelnbergCycloPalloidConicalGearSetPowerFlow
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_power_flow(
        self: "CastSelf",
    ) -> "_4418.KlingelnbergCycloPalloidHypoidGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4418

        return self.__parent__._cast(_4418.KlingelnbergCycloPalloidHypoidGearPowerFlow)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_power_flow(
        self: "CastSelf",
    ) -> "_4419.KlingelnbergCycloPalloidHypoidGearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4419

        return self.__parent__._cast(
            _4419.KlingelnbergCycloPalloidHypoidGearSetPowerFlow
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_power_flow(
        self: "CastSelf",
    ) -> "_4421.KlingelnbergCycloPalloidSpiralBevelGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4421

        return self.__parent__._cast(
            _4421.KlingelnbergCycloPalloidSpiralBevelGearPowerFlow
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_power_flow(
        self: "CastSelf",
    ) -> "_4422.KlingelnbergCycloPalloidSpiralBevelGearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4422

        return self.__parent__._cast(
            _4422.KlingelnbergCycloPalloidSpiralBevelGearSetPowerFlow
        )

    @property
    def mass_disc_power_flow(self: "CastSelf") -> "_4423.MassDiscPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4423

        return self.__parent__._cast(_4423.MassDiscPowerFlow)

    @property
    def measurement_component_power_flow(
        self: "CastSelf",
    ) -> "_4424.MeasurementComponentPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4424

        return self.__parent__._cast(_4424.MeasurementComponentPowerFlow)

    @property
    def microphone_array_power_flow(
        self: "CastSelf",
    ) -> "_4425.MicrophoneArrayPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4425

        return self.__parent__._cast(_4425.MicrophoneArrayPowerFlow)

    @property
    def microphone_power_flow(self: "CastSelf") -> "_4426.MicrophonePowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4426

        return self.__parent__._cast(_4426.MicrophonePowerFlow)

    @property
    def mountable_component_power_flow(
        self: "CastSelf",
    ) -> "_4427.MountableComponentPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4427

        return self.__parent__._cast(_4427.MountableComponentPowerFlow)

    @property
    def oil_seal_power_flow(self: "CastSelf") -> "_4428.OilSealPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4428

        return self.__parent__._cast(_4428.OilSealPowerFlow)

    @property
    def part_power_flow(self: "CastSelf") -> "_4429.PartPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4429

        return self.__parent__._cast(_4429.PartPowerFlow)

    @property
    def part_to_part_shear_coupling_half_power_flow(
        self: "CastSelf",
    ) -> "_4431.PartToPartShearCouplingHalfPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4431

        return self.__parent__._cast(_4431.PartToPartShearCouplingHalfPowerFlow)

    @property
    def part_to_part_shear_coupling_power_flow(
        self: "CastSelf",
    ) -> "_4432.PartToPartShearCouplingPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4432

        return self.__parent__._cast(_4432.PartToPartShearCouplingPowerFlow)

    @property
    def planetary_gear_set_power_flow(
        self: "CastSelf",
    ) -> "_4434.PlanetaryGearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4434

        return self.__parent__._cast(_4434.PlanetaryGearSetPowerFlow)

    @property
    def planet_carrier_power_flow(self: "CastSelf") -> "_4435.PlanetCarrierPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4435

        return self.__parent__._cast(_4435.PlanetCarrierPowerFlow)

    @property
    def point_load_power_flow(self: "CastSelf") -> "_4436.PointLoadPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4436

        return self.__parent__._cast(_4436.PointLoadPowerFlow)

    @property
    def power_load_power_flow(self: "CastSelf") -> "_4439.PowerLoadPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4439

        return self.__parent__._cast(_4439.PowerLoadPowerFlow)

    @property
    def pulley_power_flow(self: "CastSelf") -> "_4440.PulleyPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4440

        return self.__parent__._cast(_4440.PulleyPowerFlow)

    @property
    def ring_pins_power_flow(self: "CastSelf") -> "_4441.RingPinsPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4441

        return self.__parent__._cast(_4441.RingPinsPowerFlow)

    @property
    def rolling_ring_assembly_power_flow(
        self: "CastSelf",
    ) -> "_4443.RollingRingAssemblyPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4443

        return self.__parent__._cast(_4443.RollingRingAssemblyPowerFlow)

    @property
    def rolling_ring_power_flow(self: "CastSelf") -> "_4445.RollingRingPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4445

        return self.__parent__._cast(_4445.RollingRingPowerFlow)

    @property
    def root_assembly_power_flow(self: "CastSelf") -> "_4446.RootAssemblyPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4446

        return self.__parent__._cast(_4446.RootAssemblyPowerFlow)

    @property
    def shaft_hub_connection_power_flow(
        self: "CastSelf",
    ) -> "_4447.ShaftHubConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4447

        return self.__parent__._cast(_4447.ShaftHubConnectionPowerFlow)

    @property
    def shaft_power_flow(self: "CastSelf") -> "_4448.ShaftPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4448

        return self.__parent__._cast(_4448.ShaftPowerFlow)

    @property
    def specialised_assembly_power_flow(
        self: "CastSelf",
    ) -> "_4450.SpecialisedAssemblyPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4450

        return self.__parent__._cast(_4450.SpecialisedAssemblyPowerFlow)

    @property
    def spiral_bevel_gear_power_flow(
        self: "CastSelf",
    ) -> "_4452.SpiralBevelGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4452

        return self.__parent__._cast(_4452.SpiralBevelGearPowerFlow)

    @property
    def spiral_bevel_gear_set_power_flow(
        self: "CastSelf",
    ) -> "_4453.SpiralBevelGearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4453

        return self.__parent__._cast(_4453.SpiralBevelGearSetPowerFlow)

    @property
    def spring_damper_half_power_flow(
        self: "CastSelf",
    ) -> "_4455.SpringDamperHalfPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4455

        return self.__parent__._cast(_4455.SpringDamperHalfPowerFlow)

    @property
    def spring_damper_power_flow(self: "CastSelf") -> "_4456.SpringDamperPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4456

        return self.__parent__._cast(_4456.SpringDamperPowerFlow)

    @property
    def straight_bevel_diff_gear_power_flow(
        self: "CastSelf",
    ) -> "_4458.StraightBevelDiffGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4458

        return self.__parent__._cast(_4458.StraightBevelDiffGearPowerFlow)

    @property
    def straight_bevel_diff_gear_set_power_flow(
        self: "CastSelf",
    ) -> "_4459.StraightBevelDiffGearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4459

        return self.__parent__._cast(_4459.StraightBevelDiffGearSetPowerFlow)

    @property
    def straight_bevel_gear_power_flow(
        self: "CastSelf",
    ) -> "_4461.StraightBevelGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4461

        return self.__parent__._cast(_4461.StraightBevelGearPowerFlow)

    @property
    def straight_bevel_gear_set_power_flow(
        self: "CastSelf",
    ) -> "_4462.StraightBevelGearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4462

        return self.__parent__._cast(_4462.StraightBevelGearSetPowerFlow)

    @property
    def straight_bevel_planet_gear_power_flow(
        self: "CastSelf",
    ) -> "_4463.StraightBevelPlanetGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4463

        return self.__parent__._cast(_4463.StraightBevelPlanetGearPowerFlow)

    @property
    def straight_bevel_sun_gear_power_flow(
        self: "CastSelf",
    ) -> "_4464.StraightBevelSunGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4464

        return self.__parent__._cast(_4464.StraightBevelSunGearPowerFlow)

    @property
    def synchroniser_half_power_flow(
        self: "CastSelf",
    ) -> "_4465.SynchroniserHalfPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4465

        return self.__parent__._cast(_4465.SynchroniserHalfPowerFlow)

    @property
    def synchroniser_part_power_flow(
        self: "CastSelf",
    ) -> "_4466.SynchroniserPartPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4466

        return self.__parent__._cast(_4466.SynchroniserPartPowerFlow)

    @property
    def synchroniser_power_flow(self: "CastSelf") -> "_4467.SynchroniserPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4467

        return self.__parent__._cast(_4467.SynchroniserPowerFlow)

    @property
    def synchroniser_sleeve_power_flow(
        self: "CastSelf",
    ) -> "_4468.SynchroniserSleevePowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4468

        return self.__parent__._cast(_4468.SynchroniserSleevePowerFlow)

    @property
    def torque_converter_power_flow(
        self: "CastSelf",
    ) -> "_4471.TorqueConverterPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4471

        return self.__parent__._cast(_4471.TorqueConverterPowerFlow)

    @property
    def torque_converter_pump_power_flow(
        self: "CastSelf",
    ) -> "_4472.TorqueConverterPumpPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4472

        return self.__parent__._cast(_4472.TorqueConverterPumpPowerFlow)

    @property
    def torque_converter_turbine_power_flow(
        self: "CastSelf",
    ) -> "_4473.TorqueConverterTurbinePowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4473

        return self.__parent__._cast(_4473.TorqueConverterTurbinePowerFlow)

    @property
    def unbalanced_mass_power_flow(self: "CastSelf") -> "_4474.UnbalancedMassPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4474

        return self.__parent__._cast(_4474.UnbalancedMassPowerFlow)

    @property
    def virtual_component_power_flow(
        self: "CastSelf",
    ) -> "_4475.VirtualComponentPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4475

        return self.__parent__._cast(_4475.VirtualComponentPowerFlow)

    @property
    def worm_gear_power_flow(self: "CastSelf") -> "_4477.WormGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4477

        return self.__parent__._cast(_4477.WormGearPowerFlow)

    @property
    def worm_gear_set_power_flow(self: "CastSelf") -> "_4478.WormGearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4478

        return self.__parent__._cast(_4478.WormGearSetPowerFlow)

    @property
    def zerol_bevel_gear_power_flow(
        self: "CastSelf",
    ) -> "_4480.ZerolBevelGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4480

        return self.__parent__._cast(_4480.ZerolBevelGearPowerFlow)

    @property
    def zerol_bevel_gear_set_power_flow(
        self: "CastSelf",
    ) -> "_4481.ZerolBevelGearSetPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4481

        return self.__parent__._cast(_4481.ZerolBevelGearSetPowerFlow)

    @property
    def abstract_assembly_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4613.AbstractAssemblyParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4613,
        )

        return self.__parent__._cast(_4613.AbstractAssemblyParametricStudyTool)

    @property
    def abstract_shaft_or_housing_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4614.AbstractShaftOrHousingParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4614,
        )

        return self.__parent__._cast(_4614.AbstractShaftOrHousingParametricStudyTool)

    @property
    def abstract_shaft_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4615.AbstractShaftParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4615,
        )

        return self.__parent__._cast(_4615.AbstractShaftParametricStudyTool)

    @property
    def agma_gleason_conical_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4618.AGMAGleasonConicalGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4618,
        )

        return self.__parent__._cast(_4618.AGMAGleasonConicalGearParametricStudyTool)

    @property
    def agma_gleason_conical_gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4619.AGMAGleasonConicalGearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4619,
        )

        return self.__parent__._cast(_4619.AGMAGleasonConicalGearSetParametricStudyTool)

    @property
    def assembly_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4620.AssemblyParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4620,
        )

        return self.__parent__._cast(_4620.AssemblyParametricStudyTool)

    @property
    def bearing_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4621.BearingParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4621,
        )

        return self.__parent__._cast(_4621.BearingParametricStudyTool)

    @property
    def belt_drive_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4623.BeltDriveParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4623,
        )

        return self.__parent__._cast(_4623.BeltDriveParametricStudyTool)

    @property
    def bevel_differential_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4625.BevelDifferentialGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4625,
        )

        return self.__parent__._cast(_4625.BevelDifferentialGearParametricStudyTool)

    @property
    def bevel_differential_gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4626.BevelDifferentialGearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4626,
        )

        return self.__parent__._cast(_4626.BevelDifferentialGearSetParametricStudyTool)

    @property
    def bevel_differential_planet_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4627.BevelDifferentialPlanetGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4627,
        )

        return self.__parent__._cast(
            _4627.BevelDifferentialPlanetGearParametricStudyTool
        )

    @property
    def bevel_differential_sun_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4628.BevelDifferentialSunGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4628,
        )

        return self.__parent__._cast(_4628.BevelDifferentialSunGearParametricStudyTool)

    @property
    def bevel_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4630.BevelGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4630,
        )

        return self.__parent__._cast(_4630.BevelGearParametricStudyTool)

    @property
    def bevel_gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4631.BevelGearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4631,
        )

        return self.__parent__._cast(_4631.BevelGearSetParametricStudyTool)

    @property
    def bolted_joint_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4632.BoltedJointParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4632,
        )

        return self.__parent__._cast(_4632.BoltedJointParametricStudyTool)

    @property
    def bolt_parametric_study_tool(self: "CastSelf") -> "_4633.BoltParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4633,
        )

        return self.__parent__._cast(_4633.BoltParametricStudyTool)

    @property
    def clutch_half_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4635.ClutchHalfParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4635,
        )

        return self.__parent__._cast(_4635.ClutchHalfParametricStudyTool)

    @property
    def clutch_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4636.ClutchParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4636,
        )

        return self.__parent__._cast(_4636.ClutchParametricStudyTool)

    @property
    def component_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4638.ComponentParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4638,
        )

        return self.__parent__._cast(_4638.ComponentParametricStudyTool)

    @property
    def concept_coupling_half_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4640.ConceptCouplingHalfParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4640,
        )

        return self.__parent__._cast(_4640.ConceptCouplingHalfParametricStudyTool)

    @property
    def concept_coupling_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4641.ConceptCouplingParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4641,
        )

        return self.__parent__._cast(_4641.ConceptCouplingParametricStudyTool)

    @property
    def concept_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4643.ConceptGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4643,
        )

        return self.__parent__._cast(_4643.ConceptGearParametricStudyTool)

    @property
    def concept_gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4644.ConceptGearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4644,
        )

        return self.__parent__._cast(_4644.ConceptGearSetParametricStudyTool)

    @property
    def conical_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4646.ConicalGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4646,
        )

        return self.__parent__._cast(_4646.ConicalGearParametricStudyTool)

    @property
    def conical_gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4647.ConicalGearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4647,
        )

        return self.__parent__._cast(_4647.ConicalGearSetParametricStudyTool)

    @property
    def connector_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4649.ConnectorParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4649,
        )

        return self.__parent__._cast(_4649.ConnectorParametricStudyTool)

    @property
    def coupling_half_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4651.CouplingHalfParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4651,
        )

        return self.__parent__._cast(_4651.CouplingHalfParametricStudyTool)

    @property
    def coupling_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4652.CouplingParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4652,
        )

        return self.__parent__._cast(_4652.CouplingParametricStudyTool)

    @property
    def cvt_parametric_study_tool(self: "CastSelf") -> "_4654.CVTParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4654,
        )

        return self.__parent__._cast(_4654.CVTParametricStudyTool)

    @property
    def cvt_pulley_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4655.CVTPulleyParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4655,
        )

        return self.__parent__._cast(_4655.CVTPulleyParametricStudyTool)

    @property
    def cycloidal_assembly_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4656.CycloidalAssemblyParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4656,
        )

        return self.__parent__._cast(_4656.CycloidalAssemblyParametricStudyTool)

    @property
    def cycloidal_disc_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4658.CycloidalDiscParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4658,
        )

        return self.__parent__._cast(_4658.CycloidalDiscParametricStudyTool)

    @property
    def cylindrical_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4661.CylindricalGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4661,
        )

        return self.__parent__._cast(_4661.CylindricalGearParametricStudyTool)

    @property
    def cylindrical_gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4662.CylindricalGearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4662,
        )

        return self.__parent__._cast(_4662.CylindricalGearSetParametricStudyTool)

    @property
    def cylindrical_planet_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4663.CylindricalPlanetGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4663,
        )

        return self.__parent__._cast(_4663.CylindricalPlanetGearParametricStudyTool)

    @property
    def datum_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4664.DatumParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4664,
        )

        return self.__parent__._cast(_4664.DatumParametricStudyTool)

    @property
    def external_cad_model_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4672.ExternalCADModelParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4672,
        )

        return self.__parent__._cast(_4672.ExternalCADModelParametricStudyTool)

    @property
    def face_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4674.FaceGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4674,
        )

        return self.__parent__._cast(_4674.FaceGearParametricStudyTool)

    @property
    def face_gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4675.FaceGearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4675,
        )

        return self.__parent__._cast(_4675.FaceGearSetParametricStudyTool)

    @property
    def fe_part_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4676.FEPartParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4676,
        )

        return self.__parent__._cast(_4676.FEPartParametricStudyTool)

    @property
    def flexible_pin_assembly_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4677.FlexiblePinAssemblyParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4677,
        )

        return self.__parent__._cast(_4677.FlexiblePinAssemblyParametricStudyTool)

    @property
    def gear_parametric_study_tool(self: "CastSelf") -> "_4679.GearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4679,
        )

        return self.__parent__._cast(_4679.GearParametricStudyTool)

    @property
    def gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4680.GearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4680,
        )

        return self.__parent__._cast(_4680.GearSetParametricStudyTool)

    @property
    def guide_dxf_model_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4681.GuideDxfModelParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4681,
        )

        return self.__parent__._cast(_4681.GuideDxfModelParametricStudyTool)

    @property
    def hypoid_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4683.HypoidGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4683,
        )

        return self.__parent__._cast(_4683.HypoidGearParametricStudyTool)

    @property
    def hypoid_gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4684.HypoidGearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4684,
        )

        return self.__parent__._cast(_4684.HypoidGearSetParametricStudyTool)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4687.KlingelnbergCycloPalloidConicalGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4687,
        )

        return self.__parent__._cast(
            _4687.KlingelnbergCycloPalloidConicalGearParametricStudyTool
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4688.KlingelnbergCycloPalloidConicalGearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4688,
        )

        return self.__parent__._cast(
            _4688.KlingelnbergCycloPalloidConicalGearSetParametricStudyTool
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4690.KlingelnbergCycloPalloidHypoidGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4690,
        )

        return self.__parent__._cast(
            _4690.KlingelnbergCycloPalloidHypoidGearParametricStudyTool
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4691.KlingelnbergCycloPalloidHypoidGearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4691,
        )

        return self.__parent__._cast(
            _4691.KlingelnbergCycloPalloidHypoidGearSetParametricStudyTool
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4693.KlingelnbergCycloPalloidSpiralBevelGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4693,
        )

        return self.__parent__._cast(
            _4693.KlingelnbergCycloPalloidSpiralBevelGearParametricStudyTool
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4694.KlingelnbergCycloPalloidSpiralBevelGearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4694,
        )

        return self.__parent__._cast(
            _4694.KlingelnbergCycloPalloidSpiralBevelGearSetParametricStudyTool
        )

    @property
    def mass_disc_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4695.MassDiscParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4695,
        )

        return self.__parent__._cast(_4695.MassDiscParametricStudyTool)

    @property
    def measurement_component_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4696.MeasurementComponentParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4696,
        )

        return self.__parent__._cast(_4696.MeasurementComponentParametricStudyTool)

    @property
    def microphone_array_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4697.MicrophoneArrayParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4697,
        )

        return self.__parent__._cast(_4697.MicrophoneArrayParametricStudyTool)

    @property
    def microphone_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4698.MicrophoneParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4698,
        )

        return self.__parent__._cast(_4698.MicrophoneParametricStudyTool)

    @property
    def mountable_component_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4700.MountableComponentParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4700,
        )

        return self.__parent__._cast(_4700.MountableComponentParametricStudyTool)

    @property
    def oil_seal_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4701.OilSealParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4701,
        )

        return self.__parent__._cast(_4701.OilSealParametricStudyTool)

    @property
    def part_parametric_study_tool(self: "CastSelf") -> "_4713.PartParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4713,
        )

        return self.__parent__._cast(_4713.PartParametricStudyTool)

    @property
    def part_to_part_shear_coupling_half_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4715.PartToPartShearCouplingHalfParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4715,
        )

        return self.__parent__._cast(
            _4715.PartToPartShearCouplingHalfParametricStudyTool
        )

    @property
    def part_to_part_shear_coupling_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4716.PartToPartShearCouplingParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4716,
        )

        return self.__parent__._cast(_4716.PartToPartShearCouplingParametricStudyTool)

    @property
    def planetary_gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4718.PlanetaryGearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4718,
        )

        return self.__parent__._cast(_4718.PlanetaryGearSetParametricStudyTool)

    @property
    def planet_carrier_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4719.PlanetCarrierParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4719,
        )

        return self.__parent__._cast(_4719.PlanetCarrierParametricStudyTool)

    @property
    def point_load_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4720.PointLoadParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4720,
        )

        return self.__parent__._cast(_4720.PointLoadParametricStudyTool)

    @property
    def power_load_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4721.PowerLoadParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4721,
        )

        return self.__parent__._cast(_4721.PowerLoadParametricStudyTool)

    @property
    def pulley_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4722.PulleyParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4722,
        )

        return self.__parent__._cast(_4722.PulleyParametricStudyTool)

    @property
    def ring_pins_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4723.RingPinsParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4723,
        )

        return self.__parent__._cast(_4723.RingPinsParametricStudyTool)

    @property
    def rolling_ring_assembly_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4725.RollingRingAssemblyParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4725,
        )

        return self.__parent__._cast(_4725.RollingRingAssemblyParametricStudyTool)

    @property
    def rolling_ring_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4727.RollingRingParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4727,
        )

        return self.__parent__._cast(_4727.RollingRingParametricStudyTool)

    @property
    def root_assembly_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4728.RootAssemblyParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4728,
        )

        return self.__parent__._cast(_4728.RootAssemblyParametricStudyTool)

    @property
    def shaft_hub_connection_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4729.ShaftHubConnectionParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4729,
        )

        return self.__parent__._cast(_4729.ShaftHubConnectionParametricStudyTool)

    @property
    def shaft_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4730.ShaftParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4730,
        )

        return self.__parent__._cast(_4730.ShaftParametricStudyTool)

    @property
    def specialised_assembly_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4732.SpecialisedAssemblyParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4732,
        )

        return self.__parent__._cast(_4732.SpecialisedAssemblyParametricStudyTool)

    @property
    def spiral_bevel_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4734.SpiralBevelGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4734,
        )

        return self.__parent__._cast(_4734.SpiralBevelGearParametricStudyTool)

    @property
    def spiral_bevel_gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4735.SpiralBevelGearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4735,
        )

        return self.__parent__._cast(_4735.SpiralBevelGearSetParametricStudyTool)

    @property
    def spring_damper_half_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4737.SpringDamperHalfParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4737,
        )

        return self.__parent__._cast(_4737.SpringDamperHalfParametricStudyTool)

    @property
    def spring_damper_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4738.SpringDamperParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4738,
        )

        return self.__parent__._cast(_4738.SpringDamperParametricStudyTool)

    @property
    def straight_bevel_diff_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4740.StraightBevelDiffGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4740,
        )

        return self.__parent__._cast(_4740.StraightBevelDiffGearParametricStudyTool)

    @property
    def straight_bevel_diff_gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4741.StraightBevelDiffGearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4741,
        )

        return self.__parent__._cast(_4741.StraightBevelDiffGearSetParametricStudyTool)

    @property
    def straight_bevel_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4743.StraightBevelGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4743,
        )

        return self.__parent__._cast(_4743.StraightBevelGearParametricStudyTool)

    @property
    def straight_bevel_gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4744.StraightBevelGearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4744,
        )

        return self.__parent__._cast(_4744.StraightBevelGearSetParametricStudyTool)

    @property
    def straight_bevel_planet_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4745.StraightBevelPlanetGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4745,
        )

        return self.__parent__._cast(_4745.StraightBevelPlanetGearParametricStudyTool)

    @property
    def straight_bevel_sun_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4746.StraightBevelSunGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4746,
        )

        return self.__parent__._cast(_4746.StraightBevelSunGearParametricStudyTool)

    @property
    def synchroniser_half_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4747.SynchroniserHalfParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4747,
        )

        return self.__parent__._cast(_4747.SynchroniserHalfParametricStudyTool)

    @property
    def synchroniser_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4748.SynchroniserParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4748,
        )

        return self.__parent__._cast(_4748.SynchroniserParametricStudyTool)

    @property
    def synchroniser_part_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4749.SynchroniserPartParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4749,
        )

        return self.__parent__._cast(_4749.SynchroniserPartParametricStudyTool)

    @property
    def synchroniser_sleeve_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4750.SynchroniserSleeveParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4750,
        )

        return self.__parent__._cast(_4750.SynchroniserSleeveParametricStudyTool)

    @property
    def torque_converter_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4752.TorqueConverterParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4752,
        )

        return self.__parent__._cast(_4752.TorqueConverterParametricStudyTool)

    @property
    def torque_converter_pump_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4753.TorqueConverterPumpParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4753,
        )

        return self.__parent__._cast(_4753.TorqueConverterPumpParametricStudyTool)

    @property
    def torque_converter_turbine_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4754.TorqueConverterTurbineParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4754,
        )

        return self.__parent__._cast(_4754.TorqueConverterTurbineParametricStudyTool)

    @property
    def unbalanced_mass_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4755.UnbalancedMassParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4755,
        )

        return self.__parent__._cast(_4755.UnbalancedMassParametricStudyTool)

    @property
    def virtual_component_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4756.VirtualComponentParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4756,
        )

        return self.__parent__._cast(_4756.VirtualComponentParametricStudyTool)

    @property
    def worm_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4758.WormGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4758,
        )

        return self.__parent__._cast(_4758.WormGearParametricStudyTool)

    @property
    def worm_gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4759.WormGearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4759,
        )

        return self.__parent__._cast(_4759.WormGearSetParametricStudyTool)

    @property
    def zerol_bevel_gear_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4761.ZerolBevelGearParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4761,
        )

        return self.__parent__._cast(_4761.ZerolBevelGearParametricStudyTool)

    @property
    def zerol_bevel_gear_set_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4762.ZerolBevelGearSetParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4762,
        )

        return self.__parent__._cast(_4762.ZerolBevelGearSetParametricStudyTool)

    @property
    def abstract_assembly_modal_analysis(
        self: "CastSelf",
    ) -> "_4894.AbstractAssemblyModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4894,
        )

        return self.__parent__._cast(_4894.AbstractAssemblyModalAnalysis)

    @property
    def abstract_shaft_modal_analysis(
        self: "CastSelf",
    ) -> "_4895.AbstractShaftModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4895,
        )

        return self.__parent__._cast(_4895.AbstractShaftModalAnalysis)

    @property
    def abstract_shaft_or_housing_modal_analysis(
        self: "CastSelf",
    ) -> "_4896.AbstractShaftOrHousingModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4896,
        )

        return self.__parent__._cast(_4896.AbstractShaftOrHousingModalAnalysis)

    @property
    def agma_gleason_conical_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4899.AGMAGleasonConicalGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4899,
        )

        return self.__parent__._cast(_4899.AGMAGleasonConicalGearModalAnalysis)

    @property
    def agma_gleason_conical_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_4900.AGMAGleasonConicalGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4900,
        )

        return self.__parent__._cast(_4900.AGMAGleasonConicalGearSetModalAnalysis)

    @property
    def assembly_modal_analysis(self: "CastSelf") -> "_4901.AssemblyModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4901,
        )

        return self.__parent__._cast(_4901.AssemblyModalAnalysis)

    @property
    def bearing_modal_analysis(self: "CastSelf") -> "_4902.BearingModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4902,
        )

        return self.__parent__._cast(_4902.BearingModalAnalysis)

    @property
    def belt_drive_modal_analysis(self: "CastSelf") -> "_4904.BeltDriveModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4904,
        )

        return self.__parent__._cast(_4904.BeltDriveModalAnalysis)

    @property
    def bevel_differential_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4906.BevelDifferentialGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4906,
        )

        return self.__parent__._cast(_4906.BevelDifferentialGearModalAnalysis)

    @property
    def bevel_differential_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_4907.BevelDifferentialGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4907,
        )

        return self.__parent__._cast(_4907.BevelDifferentialGearSetModalAnalysis)

    @property
    def bevel_differential_planet_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4908.BevelDifferentialPlanetGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4908,
        )

        return self.__parent__._cast(_4908.BevelDifferentialPlanetGearModalAnalysis)

    @property
    def bevel_differential_sun_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4909.BevelDifferentialSunGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4909,
        )

        return self.__parent__._cast(_4909.BevelDifferentialSunGearModalAnalysis)

    @property
    def bevel_gear_modal_analysis(self: "CastSelf") -> "_4911.BevelGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4911,
        )

        return self.__parent__._cast(_4911.BevelGearModalAnalysis)

    @property
    def bevel_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_4912.BevelGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4912,
        )

        return self.__parent__._cast(_4912.BevelGearSetModalAnalysis)

    @property
    def bolted_joint_modal_analysis(
        self: "CastSelf",
    ) -> "_4913.BoltedJointModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4913,
        )

        return self.__parent__._cast(_4913.BoltedJointModalAnalysis)

    @property
    def bolt_modal_analysis(self: "CastSelf") -> "_4914.BoltModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4914,
        )

        return self.__parent__._cast(_4914.BoltModalAnalysis)

    @property
    def clutch_half_modal_analysis(self: "CastSelf") -> "_4916.ClutchHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4916,
        )

        return self.__parent__._cast(_4916.ClutchHalfModalAnalysis)

    @property
    def clutch_modal_analysis(self: "CastSelf") -> "_4917.ClutchModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4917,
        )

        return self.__parent__._cast(_4917.ClutchModalAnalysis)

    @property
    def component_modal_analysis(self: "CastSelf") -> "_4919.ComponentModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4919,
        )

        return self.__parent__._cast(_4919.ComponentModalAnalysis)

    @property
    def concept_coupling_half_modal_analysis(
        self: "CastSelf",
    ) -> "_4921.ConceptCouplingHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4921,
        )

        return self.__parent__._cast(_4921.ConceptCouplingHalfModalAnalysis)

    @property
    def concept_coupling_modal_analysis(
        self: "CastSelf",
    ) -> "_4922.ConceptCouplingModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4922,
        )

        return self.__parent__._cast(_4922.ConceptCouplingModalAnalysis)

    @property
    def concept_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4924.ConceptGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4924,
        )

        return self.__parent__._cast(_4924.ConceptGearModalAnalysis)

    @property
    def concept_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_4925.ConceptGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4925,
        )

        return self.__parent__._cast(_4925.ConceptGearSetModalAnalysis)

    @property
    def conical_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4927.ConicalGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4927,
        )

        return self.__parent__._cast(_4927.ConicalGearModalAnalysis)

    @property
    def conical_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_4928.ConicalGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4928,
        )

        return self.__parent__._cast(_4928.ConicalGearSetModalAnalysis)

    @property
    def connector_modal_analysis(self: "CastSelf") -> "_4930.ConnectorModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4930,
        )

        return self.__parent__._cast(_4930.ConnectorModalAnalysis)

    @property
    def coupling_half_modal_analysis(
        self: "CastSelf",
    ) -> "_4933.CouplingHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4933,
        )

        return self.__parent__._cast(_4933.CouplingHalfModalAnalysis)

    @property
    def coupling_modal_analysis(self: "CastSelf") -> "_4934.CouplingModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4934,
        )

        return self.__parent__._cast(_4934.CouplingModalAnalysis)

    @property
    def cvt_modal_analysis(self: "CastSelf") -> "_4936.CVTModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4936,
        )

        return self.__parent__._cast(_4936.CVTModalAnalysis)

    @property
    def cvt_pulley_modal_analysis(self: "CastSelf") -> "_4937.CVTPulleyModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4937,
        )

        return self.__parent__._cast(_4937.CVTPulleyModalAnalysis)

    @property
    def cycloidal_assembly_modal_analysis(
        self: "CastSelf",
    ) -> "_4938.CycloidalAssemblyModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4938,
        )

        return self.__parent__._cast(_4938.CycloidalAssemblyModalAnalysis)

    @property
    def cycloidal_disc_modal_analysis(
        self: "CastSelf",
    ) -> "_4940.CycloidalDiscModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4940,
        )

        return self.__parent__._cast(_4940.CycloidalDiscModalAnalysis)

    @property
    def cylindrical_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4943.CylindricalGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4943,
        )

        return self.__parent__._cast(_4943.CylindricalGearModalAnalysis)

    @property
    def cylindrical_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_4944.CylindricalGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4944,
        )

        return self.__parent__._cast(_4944.CylindricalGearSetModalAnalysis)

    @property
    def cylindrical_planet_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4945.CylindricalPlanetGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4945,
        )

        return self.__parent__._cast(_4945.CylindricalPlanetGearModalAnalysis)

    @property
    def datum_modal_analysis(self: "CastSelf") -> "_4946.DatumModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4946,
        )

        return self.__parent__._cast(_4946.DatumModalAnalysis)

    @property
    def external_cad_model_modal_analysis(
        self: "CastSelf",
    ) -> "_4950.ExternalCADModelModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4950,
        )

        return self.__parent__._cast(_4950.ExternalCADModelModalAnalysis)

    @property
    def face_gear_modal_analysis(self: "CastSelf") -> "_4952.FaceGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4952,
        )

        return self.__parent__._cast(_4952.FaceGearModalAnalysis)

    @property
    def face_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_4953.FaceGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4953,
        )

        return self.__parent__._cast(_4953.FaceGearSetModalAnalysis)

    @property
    def fe_part_modal_analysis(self: "CastSelf") -> "_4954.FEPartModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4954,
        )

        return self.__parent__._cast(_4954.FEPartModalAnalysis)

    @property
    def flexible_pin_assembly_modal_analysis(
        self: "CastSelf",
    ) -> "_4955.FlexiblePinAssemblyModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4955,
        )

        return self.__parent__._cast(_4955.FlexiblePinAssemblyModalAnalysis)

    @property
    def gear_modal_analysis(self: "CastSelf") -> "_4958.GearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4958,
        )

        return self.__parent__._cast(_4958.GearModalAnalysis)

    @property
    def gear_set_modal_analysis(self: "CastSelf") -> "_4959.GearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4959,
        )

        return self.__parent__._cast(_4959.GearSetModalAnalysis)

    @property
    def guide_dxf_model_modal_analysis(
        self: "CastSelf",
    ) -> "_4960.GuideDxfModelModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4960,
        )

        return self.__parent__._cast(_4960.GuideDxfModelModalAnalysis)

    @property
    def hypoid_gear_modal_analysis(self: "CastSelf") -> "_4962.HypoidGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4962,
        )

        return self.__parent__._cast(_4962.HypoidGearModalAnalysis)

    @property
    def hypoid_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_4963.HypoidGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4963,
        )

        return self.__parent__._cast(_4963.HypoidGearSetModalAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4966.KlingelnbergCycloPalloidConicalGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4966,
        )

        return self.__parent__._cast(
            _4966.KlingelnbergCycloPalloidConicalGearModalAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_4967.KlingelnbergCycloPalloidConicalGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4967,
        )

        return self.__parent__._cast(
            _4967.KlingelnbergCycloPalloidConicalGearSetModalAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4969.KlingelnbergCycloPalloidHypoidGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4969,
        )

        return self.__parent__._cast(
            _4969.KlingelnbergCycloPalloidHypoidGearModalAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_4970.KlingelnbergCycloPalloidHypoidGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4970,
        )

        return self.__parent__._cast(
            _4970.KlingelnbergCycloPalloidHypoidGearSetModalAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4972.KlingelnbergCycloPalloidSpiralBevelGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4972,
        )

        return self.__parent__._cast(
            _4972.KlingelnbergCycloPalloidSpiralBevelGearModalAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_4973.KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4973,
        )

        return self.__parent__._cast(
            _4973.KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysis
        )

    @property
    def mass_disc_modal_analysis(self: "CastSelf") -> "_4974.MassDiscModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4974,
        )

        return self.__parent__._cast(_4974.MassDiscModalAnalysis)

    @property
    def measurement_component_modal_analysis(
        self: "CastSelf",
    ) -> "_4975.MeasurementComponentModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4975,
        )

        return self.__parent__._cast(_4975.MeasurementComponentModalAnalysis)

    @property
    def microphone_array_modal_analysis(
        self: "CastSelf",
    ) -> "_4976.MicrophoneArrayModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4976,
        )

        return self.__parent__._cast(_4976.MicrophoneArrayModalAnalysis)

    @property
    def microphone_modal_analysis(self: "CastSelf") -> "_4977.MicrophoneModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4977,
        )

        return self.__parent__._cast(_4977.MicrophoneModalAnalysis)

    @property
    def mountable_component_modal_analysis(
        self: "CastSelf",
    ) -> "_4983.MountableComponentModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4983,
        )

        return self.__parent__._cast(_4983.MountableComponentModalAnalysis)

    @property
    def oil_seal_modal_analysis(self: "CastSelf") -> "_4985.OilSealModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4985,
        )

        return self.__parent__._cast(_4985.OilSealModalAnalysis)

    @property
    def part_modal_analysis(self: "CastSelf") -> "_4987.PartModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4987,
        )

        return self.__parent__._cast(_4987.PartModalAnalysis)

    @property
    def part_to_part_shear_coupling_half_modal_analysis(
        self: "CastSelf",
    ) -> "_4989.PartToPartShearCouplingHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4989,
        )

        return self.__parent__._cast(_4989.PartToPartShearCouplingHalfModalAnalysis)

    @property
    def part_to_part_shear_coupling_modal_analysis(
        self: "CastSelf",
    ) -> "_4990.PartToPartShearCouplingModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4990,
        )

        return self.__parent__._cast(_4990.PartToPartShearCouplingModalAnalysis)

    @property
    def planetary_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_4992.PlanetaryGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4992,
        )

        return self.__parent__._cast(_4992.PlanetaryGearSetModalAnalysis)

    @property
    def planet_carrier_modal_analysis(
        self: "CastSelf",
    ) -> "_4993.PlanetCarrierModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4993,
        )

        return self.__parent__._cast(_4993.PlanetCarrierModalAnalysis)

    @property
    def point_load_modal_analysis(self: "CastSelf") -> "_4994.PointLoadModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4994,
        )

        return self.__parent__._cast(_4994.PointLoadModalAnalysis)

    @property
    def power_load_modal_analysis(self: "CastSelf") -> "_4995.PowerLoadModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4995,
        )

        return self.__parent__._cast(_4995.PowerLoadModalAnalysis)

    @property
    def pulley_modal_analysis(self: "CastSelf") -> "_4996.PulleyModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4996,
        )

        return self.__parent__._cast(_4996.PulleyModalAnalysis)

    @property
    def ring_pins_modal_analysis(self: "CastSelf") -> "_4997.RingPinsModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4997,
        )

        return self.__parent__._cast(_4997.RingPinsModalAnalysis)

    @property
    def rolling_ring_assembly_modal_analysis(
        self: "CastSelf",
    ) -> "_4999.RollingRingAssemblyModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4999,
        )

        return self.__parent__._cast(_4999.RollingRingAssemblyModalAnalysis)

    @property
    def rolling_ring_modal_analysis(
        self: "CastSelf",
    ) -> "_5001.RollingRingModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5001,
        )

        return self.__parent__._cast(_5001.RollingRingModalAnalysis)

    @property
    def root_assembly_modal_analysis(
        self: "CastSelf",
    ) -> "_5002.RootAssemblyModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5002,
        )

        return self.__parent__._cast(_5002.RootAssemblyModalAnalysis)

    @property
    def shaft_hub_connection_modal_analysis(
        self: "CastSelf",
    ) -> "_5003.ShaftHubConnectionModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5003,
        )

        return self.__parent__._cast(_5003.ShaftHubConnectionModalAnalysis)

    @property
    def shaft_modal_analysis(self: "CastSelf") -> "_5004.ShaftModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5004,
        )

        return self.__parent__._cast(_5004.ShaftModalAnalysis)

    @property
    def specialised_assembly_modal_analysis(
        self: "CastSelf",
    ) -> "_5007.SpecialisedAssemblyModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5007,
        )

        return self.__parent__._cast(_5007.SpecialisedAssemblyModalAnalysis)

    @property
    def spiral_bevel_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_5009.SpiralBevelGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5009,
        )

        return self.__parent__._cast(_5009.SpiralBevelGearModalAnalysis)

    @property
    def spiral_bevel_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_5010.SpiralBevelGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5010,
        )

        return self.__parent__._cast(_5010.SpiralBevelGearSetModalAnalysis)

    @property
    def spring_damper_half_modal_analysis(
        self: "CastSelf",
    ) -> "_5012.SpringDamperHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5012,
        )

        return self.__parent__._cast(_5012.SpringDamperHalfModalAnalysis)

    @property
    def spring_damper_modal_analysis(
        self: "CastSelf",
    ) -> "_5013.SpringDamperModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5013,
        )

        return self.__parent__._cast(_5013.SpringDamperModalAnalysis)

    @property
    def straight_bevel_diff_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_5015.StraightBevelDiffGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5015,
        )

        return self.__parent__._cast(_5015.StraightBevelDiffGearModalAnalysis)

    @property
    def straight_bevel_diff_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_5016.StraightBevelDiffGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5016,
        )

        return self.__parent__._cast(_5016.StraightBevelDiffGearSetModalAnalysis)

    @property
    def straight_bevel_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_5018.StraightBevelGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5018,
        )

        return self.__parent__._cast(_5018.StraightBevelGearModalAnalysis)

    @property
    def straight_bevel_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_5019.StraightBevelGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5019,
        )

        return self.__parent__._cast(_5019.StraightBevelGearSetModalAnalysis)

    @property
    def straight_bevel_planet_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_5020.StraightBevelPlanetGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5020,
        )

        return self.__parent__._cast(_5020.StraightBevelPlanetGearModalAnalysis)

    @property
    def straight_bevel_sun_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_5021.StraightBevelSunGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5021,
        )

        return self.__parent__._cast(_5021.StraightBevelSunGearModalAnalysis)

    @property
    def synchroniser_half_modal_analysis(
        self: "CastSelf",
    ) -> "_5022.SynchroniserHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5022,
        )

        return self.__parent__._cast(_5022.SynchroniserHalfModalAnalysis)

    @property
    def synchroniser_modal_analysis(
        self: "CastSelf",
    ) -> "_5023.SynchroniserModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5023,
        )

        return self.__parent__._cast(_5023.SynchroniserModalAnalysis)

    @property
    def synchroniser_part_modal_analysis(
        self: "CastSelf",
    ) -> "_5024.SynchroniserPartModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5024,
        )

        return self.__parent__._cast(_5024.SynchroniserPartModalAnalysis)

    @property
    def synchroniser_sleeve_modal_analysis(
        self: "CastSelf",
    ) -> "_5025.SynchroniserSleeveModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5025,
        )

        return self.__parent__._cast(_5025.SynchroniserSleeveModalAnalysis)

    @property
    def torque_converter_modal_analysis(
        self: "CastSelf",
    ) -> "_5027.TorqueConverterModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5027,
        )

        return self.__parent__._cast(_5027.TorqueConverterModalAnalysis)

    @property
    def torque_converter_pump_modal_analysis(
        self: "CastSelf",
    ) -> "_5028.TorqueConverterPumpModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5028,
        )

        return self.__parent__._cast(_5028.TorqueConverterPumpModalAnalysis)

    @property
    def torque_converter_turbine_modal_analysis(
        self: "CastSelf",
    ) -> "_5029.TorqueConverterTurbineModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5029,
        )

        return self.__parent__._cast(_5029.TorqueConverterTurbineModalAnalysis)

    @property
    def unbalanced_mass_modal_analysis(
        self: "CastSelf",
    ) -> "_5030.UnbalancedMassModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5030,
        )

        return self.__parent__._cast(_5030.UnbalancedMassModalAnalysis)

    @property
    def virtual_component_modal_analysis(
        self: "CastSelf",
    ) -> "_5031.VirtualComponentModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5031,
        )

        return self.__parent__._cast(_5031.VirtualComponentModalAnalysis)

    @property
    def worm_gear_modal_analysis(self: "CastSelf") -> "_5036.WormGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5036,
        )

        return self.__parent__._cast(_5036.WormGearModalAnalysis)

    @property
    def worm_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_5037.WormGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5037,
        )

        return self.__parent__._cast(_5037.WormGearSetModalAnalysis)

    @property
    def zerol_bevel_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_5039.ZerolBevelGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5039,
        )

        return self.__parent__._cast(_5039.ZerolBevelGearModalAnalysis)

    @property
    def zerol_bevel_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_5040.ZerolBevelGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5040,
        )

        return self.__parent__._cast(_5040.ZerolBevelGearSetModalAnalysis)

    @property
    def abstract_assembly_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5184.AbstractAssemblyModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5184,
        )

        return self.__parent__._cast(_5184.AbstractAssemblyModalAnalysisAtAStiffness)

    @property
    def abstract_shaft_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5185.AbstractShaftModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5185,
        )

        return self.__parent__._cast(_5185.AbstractShaftModalAnalysisAtAStiffness)

    @property
    def abstract_shaft_or_housing_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5186.AbstractShaftOrHousingModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5186,
        )

        return self.__parent__._cast(
            _5186.AbstractShaftOrHousingModalAnalysisAtAStiffness
        )

    @property
    def agma_gleason_conical_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5189.AGMAGleasonConicalGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5189,
        )

        return self.__parent__._cast(
            _5189.AGMAGleasonConicalGearModalAnalysisAtAStiffness
        )

    @property
    def agma_gleason_conical_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5190.AGMAGleasonConicalGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5190,
        )

        return self.__parent__._cast(
            _5190.AGMAGleasonConicalGearSetModalAnalysisAtAStiffness
        )

    @property
    def assembly_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5191.AssemblyModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5191,
        )

        return self.__parent__._cast(_5191.AssemblyModalAnalysisAtAStiffness)

    @property
    def bearing_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5192.BearingModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5192,
        )

        return self.__parent__._cast(_5192.BearingModalAnalysisAtAStiffness)

    @property
    def belt_drive_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5194.BeltDriveModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5194,
        )

        return self.__parent__._cast(_5194.BeltDriveModalAnalysisAtAStiffness)

    @property
    def bevel_differential_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5196.BevelDifferentialGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5196,
        )

        return self.__parent__._cast(
            _5196.BevelDifferentialGearModalAnalysisAtAStiffness
        )

    @property
    def bevel_differential_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5197.BevelDifferentialGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5197,
        )

        return self.__parent__._cast(
            _5197.BevelDifferentialGearSetModalAnalysisAtAStiffness
        )

    @property
    def bevel_differential_planet_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5198.BevelDifferentialPlanetGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5198,
        )

        return self.__parent__._cast(
            _5198.BevelDifferentialPlanetGearModalAnalysisAtAStiffness
        )

    @property
    def bevel_differential_sun_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5199.BevelDifferentialSunGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5199,
        )

        return self.__parent__._cast(
            _5199.BevelDifferentialSunGearModalAnalysisAtAStiffness
        )

    @property
    def bevel_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5201.BevelGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5201,
        )

        return self.__parent__._cast(_5201.BevelGearModalAnalysisAtAStiffness)

    @property
    def bevel_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5202.BevelGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5202,
        )

        return self.__parent__._cast(_5202.BevelGearSetModalAnalysisAtAStiffness)

    @property
    def bolted_joint_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5203.BoltedJointModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5203,
        )

        return self.__parent__._cast(_5203.BoltedJointModalAnalysisAtAStiffness)

    @property
    def bolt_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5204.BoltModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5204,
        )

        return self.__parent__._cast(_5204.BoltModalAnalysisAtAStiffness)

    @property
    def clutch_half_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5206.ClutchHalfModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5206,
        )

        return self.__parent__._cast(_5206.ClutchHalfModalAnalysisAtAStiffness)

    @property
    def clutch_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5207.ClutchModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5207,
        )

        return self.__parent__._cast(_5207.ClutchModalAnalysisAtAStiffness)

    @property
    def component_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5209.ComponentModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5209,
        )

        return self.__parent__._cast(_5209.ComponentModalAnalysisAtAStiffness)

    @property
    def concept_coupling_half_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5211.ConceptCouplingHalfModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5211,
        )

        return self.__parent__._cast(_5211.ConceptCouplingHalfModalAnalysisAtAStiffness)

    @property
    def concept_coupling_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5212.ConceptCouplingModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5212,
        )

        return self.__parent__._cast(_5212.ConceptCouplingModalAnalysisAtAStiffness)

    @property
    def concept_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5214.ConceptGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5214,
        )

        return self.__parent__._cast(_5214.ConceptGearModalAnalysisAtAStiffness)

    @property
    def concept_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5215.ConceptGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5215,
        )

        return self.__parent__._cast(_5215.ConceptGearSetModalAnalysisAtAStiffness)

    @property
    def conical_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5217.ConicalGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5217,
        )

        return self.__parent__._cast(_5217.ConicalGearModalAnalysisAtAStiffness)

    @property
    def conical_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5218.ConicalGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5218,
        )

        return self.__parent__._cast(_5218.ConicalGearSetModalAnalysisAtAStiffness)

    @property
    def connector_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5220.ConnectorModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5220,
        )

        return self.__parent__._cast(_5220.ConnectorModalAnalysisAtAStiffness)

    @property
    def coupling_half_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5222.CouplingHalfModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5222,
        )

        return self.__parent__._cast(_5222.CouplingHalfModalAnalysisAtAStiffness)

    @property
    def coupling_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5223.CouplingModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5223,
        )

        return self.__parent__._cast(_5223.CouplingModalAnalysisAtAStiffness)

    @property
    def cvt_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5225.CVTModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5225,
        )

        return self.__parent__._cast(_5225.CVTModalAnalysisAtAStiffness)

    @property
    def cvt_pulley_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5226.CVTPulleyModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5226,
        )

        return self.__parent__._cast(_5226.CVTPulleyModalAnalysisAtAStiffness)

    @property
    def cycloidal_assembly_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5227.CycloidalAssemblyModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5227,
        )

        return self.__parent__._cast(_5227.CycloidalAssemblyModalAnalysisAtAStiffness)

    @property
    def cycloidal_disc_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5229.CycloidalDiscModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5229,
        )

        return self.__parent__._cast(_5229.CycloidalDiscModalAnalysisAtAStiffness)

    @property
    def cylindrical_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5232.CylindricalGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5232,
        )

        return self.__parent__._cast(_5232.CylindricalGearModalAnalysisAtAStiffness)

    @property
    def cylindrical_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5233.CylindricalGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5233,
        )

        return self.__parent__._cast(_5233.CylindricalGearSetModalAnalysisAtAStiffness)

    @property
    def cylindrical_planet_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5234.CylindricalPlanetGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5234,
        )

        return self.__parent__._cast(
            _5234.CylindricalPlanetGearModalAnalysisAtAStiffness
        )

    @property
    def datum_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5235.DatumModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5235,
        )

        return self.__parent__._cast(_5235.DatumModalAnalysisAtAStiffness)

    @property
    def external_cad_model_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5237.ExternalCADModelModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5237,
        )

        return self.__parent__._cast(_5237.ExternalCADModelModalAnalysisAtAStiffness)

    @property
    def face_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5239.FaceGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5239,
        )

        return self.__parent__._cast(_5239.FaceGearModalAnalysisAtAStiffness)

    @property
    def face_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5240.FaceGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5240,
        )

        return self.__parent__._cast(_5240.FaceGearSetModalAnalysisAtAStiffness)

    @property
    def fe_part_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5241.FEPartModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5241,
        )

        return self.__parent__._cast(_5241.FEPartModalAnalysisAtAStiffness)

    @property
    def flexible_pin_assembly_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5242.FlexiblePinAssemblyModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5242,
        )

        return self.__parent__._cast(_5242.FlexiblePinAssemblyModalAnalysisAtAStiffness)

    @property
    def gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5244.GearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5244,
        )

        return self.__parent__._cast(_5244.GearModalAnalysisAtAStiffness)

    @property
    def gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5245.GearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5245,
        )

        return self.__parent__._cast(_5245.GearSetModalAnalysisAtAStiffness)

    @property
    def guide_dxf_model_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5246.GuideDxfModelModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5246,
        )

        return self.__parent__._cast(_5246.GuideDxfModelModalAnalysisAtAStiffness)

    @property
    def hypoid_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5248.HypoidGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5248,
        )

        return self.__parent__._cast(_5248.HypoidGearModalAnalysisAtAStiffness)

    @property
    def hypoid_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5249.HypoidGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5249,
        )

        return self.__parent__._cast(_5249.HypoidGearSetModalAnalysisAtAStiffness)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5252.KlingelnbergCycloPalloidConicalGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5252,
        )

        return self.__parent__._cast(
            _5252.KlingelnbergCycloPalloidConicalGearModalAnalysisAtAStiffness
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5253.KlingelnbergCycloPalloidConicalGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5253,
        )

        return self.__parent__._cast(
            _5253.KlingelnbergCycloPalloidConicalGearSetModalAnalysisAtAStiffness
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5255.KlingelnbergCycloPalloidHypoidGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5255,
        )

        return self.__parent__._cast(
            _5255.KlingelnbergCycloPalloidHypoidGearModalAnalysisAtAStiffness
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5256.KlingelnbergCycloPalloidHypoidGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5256,
        )

        return self.__parent__._cast(
            _5256.KlingelnbergCycloPalloidHypoidGearSetModalAnalysisAtAStiffness
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5258.KlingelnbergCycloPalloidSpiralBevelGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5258,
        )

        return self.__parent__._cast(
            _5258.KlingelnbergCycloPalloidSpiralBevelGearModalAnalysisAtAStiffness
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5259.KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5259,
        )

        return self.__parent__._cast(
            _5259.KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysisAtAStiffness
        )

    @property
    def mass_disc_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5260.MassDiscModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5260,
        )

        return self.__parent__._cast(_5260.MassDiscModalAnalysisAtAStiffness)

    @property
    def measurement_component_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5261.MeasurementComponentModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5261,
        )

        return self.__parent__._cast(
            _5261.MeasurementComponentModalAnalysisAtAStiffness
        )

    @property
    def microphone_array_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5262.MicrophoneArrayModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5262,
        )

        return self.__parent__._cast(_5262.MicrophoneArrayModalAnalysisAtAStiffness)

    @property
    def microphone_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5263.MicrophoneModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5263,
        )

        return self.__parent__._cast(_5263.MicrophoneModalAnalysisAtAStiffness)

    @property
    def mountable_component_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5265.MountableComponentModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5265,
        )

        return self.__parent__._cast(_5265.MountableComponentModalAnalysisAtAStiffness)

    @property
    def oil_seal_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5266.OilSealModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5266,
        )

        return self.__parent__._cast(_5266.OilSealModalAnalysisAtAStiffness)

    @property
    def part_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5267.PartModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5267,
        )

        return self.__parent__._cast(_5267.PartModalAnalysisAtAStiffness)

    @property
    def part_to_part_shear_coupling_half_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5269.PartToPartShearCouplingHalfModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5269,
        )

        return self.__parent__._cast(
            _5269.PartToPartShearCouplingHalfModalAnalysisAtAStiffness
        )

    @property
    def part_to_part_shear_coupling_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5270.PartToPartShearCouplingModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5270,
        )

        return self.__parent__._cast(
            _5270.PartToPartShearCouplingModalAnalysisAtAStiffness
        )

    @property
    def planetary_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5272.PlanetaryGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5272,
        )

        return self.__parent__._cast(_5272.PlanetaryGearSetModalAnalysisAtAStiffness)

    @property
    def planet_carrier_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5273.PlanetCarrierModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5273,
        )

        return self.__parent__._cast(_5273.PlanetCarrierModalAnalysisAtAStiffness)

    @property
    def point_load_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5274.PointLoadModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5274,
        )

        return self.__parent__._cast(_5274.PointLoadModalAnalysisAtAStiffness)

    @property
    def power_load_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5275.PowerLoadModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5275,
        )

        return self.__parent__._cast(_5275.PowerLoadModalAnalysisAtAStiffness)

    @property
    def pulley_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5276.PulleyModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5276,
        )

        return self.__parent__._cast(_5276.PulleyModalAnalysisAtAStiffness)

    @property
    def ring_pins_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5277.RingPinsModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5277,
        )

        return self.__parent__._cast(_5277.RingPinsModalAnalysisAtAStiffness)

    @property
    def rolling_ring_assembly_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5279.RollingRingAssemblyModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5279,
        )

        return self.__parent__._cast(_5279.RollingRingAssemblyModalAnalysisAtAStiffness)

    @property
    def rolling_ring_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5281.RollingRingModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5281,
        )

        return self.__parent__._cast(_5281.RollingRingModalAnalysisAtAStiffness)

    @property
    def root_assembly_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5282.RootAssemblyModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5282,
        )

        return self.__parent__._cast(_5282.RootAssemblyModalAnalysisAtAStiffness)

    @property
    def shaft_hub_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5283.ShaftHubConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5283,
        )

        return self.__parent__._cast(_5283.ShaftHubConnectionModalAnalysisAtAStiffness)

    @property
    def shaft_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5284.ShaftModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5284,
        )

        return self.__parent__._cast(_5284.ShaftModalAnalysisAtAStiffness)

    @property
    def specialised_assembly_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5286.SpecialisedAssemblyModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5286,
        )

        return self.__parent__._cast(_5286.SpecialisedAssemblyModalAnalysisAtAStiffness)

    @property
    def spiral_bevel_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5288.SpiralBevelGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5288,
        )

        return self.__parent__._cast(_5288.SpiralBevelGearModalAnalysisAtAStiffness)

    @property
    def spiral_bevel_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5289.SpiralBevelGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5289,
        )

        return self.__parent__._cast(_5289.SpiralBevelGearSetModalAnalysisAtAStiffness)

    @property
    def spring_damper_half_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5291.SpringDamperHalfModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5291,
        )

        return self.__parent__._cast(_5291.SpringDamperHalfModalAnalysisAtAStiffness)

    @property
    def spring_damper_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5292.SpringDamperModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5292,
        )

        return self.__parent__._cast(_5292.SpringDamperModalAnalysisAtAStiffness)

    @property
    def straight_bevel_diff_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5294.StraightBevelDiffGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5294,
        )

        return self.__parent__._cast(
            _5294.StraightBevelDiffGearModalAnalysisAtAStiffness
        )

    @property
    def straight_bevel_diff_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5295.StraightBevelDiffGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5295,
        )

        return self.__parent__._cast(
            _5295.StraightBevelDiffGearSetModalAnalysisAtAStiffness
        )

    @property
    def straight_bevel_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5297.StraightBevelGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5297,
        )

        return self.__parent__._cast(_5297.StraightBevelGearModalAnalysisAtAStiffness)

    @property
    def straight_bevel_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5298.StraightBevelGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5298,
        )

        return self.__parent__._cast(
            _5298.StraightBevelGearSetModalAnalysisAtAStiffness
        )

    @property
    def straight_bevel_planet_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5299.StraightBevelPlanetGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5299,
        )

        return self.__parent__._cast(
            _5299.StraightBevelPlanetGearModalAnalysisAtAStiffness
        )

    @property
    def straight_bevel_sun_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5300.StraightBevelSunGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5300,
        )

        return self.__parent__._cast(
            _5300.StraightBevelSunGearModalAnalysisAtAStiffness
        )

    @property
    def synchroniser_half_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5301.SynchroniserHalfModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5301,
        )

        return self.__parent__._cast(_5301.SynchroniserHalfModalAnalysisAtAStiffness)

    @property
    def synchroniser_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5302.SynchroniserModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5302,
        )

        return self.__parent__._cast(_5302.SynchroniserModalAnalysisAtAStiffness)

    @property
    def synchroniser_part_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5303.SynchroniserPartModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5303,
        )

        return self.__parent__._cast(_5303.SynchroniserPartModalAnalysisAtAStiffness)

    @property
    def synchroniser_sleeve_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5304.SynchroniserSleeveModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5304,
        )

        return self.__parent__._cast(_5304.SynchroniserSleeveModalAnalysisAtAStiffness)

    @property
    def torque_converter_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5306.TorqueConverterModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5306,
        )

        return self.__parent__._cast(_5306.TorqueConverterModalAnalysisAtAStiffness)

    @property
    def torque_converter_pump_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5307.TorqueConverterPumpModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5307,
        )

        return self.__parent__._cast(_5307.TorqueConverterPumpModalAnalysisAtAStiffness)

    @property
    def torque_converter_turbine_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5308.TorqueConverterTurbineModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5308,
        )

        return self.__parent__._cast(
            _5308.TorqueConverterTurbineModalAnalysisAtAStiffness
        )

    @property
    def unbalanced_mass_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5309.UnbalancedMassModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5309,
        )

        return self.__parent__._cast(_5309.UnbalancedMassModalAnalysisAtAStiffness)

    @property
    def virtual_component_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5310.VirtualComponentModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5310,
        )

        return self.__parent__._cast(_5310.VirtualComponentModalAnalysisAtAStiffness)

    @property
    def worm_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5312.WormGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5312,
        )

        return self.__parent__._cast(_5312.WormGearModalAnalysisAtAStiffness)

    @property
    def worm_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5313.WormGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5313,
        )

        return self.__parent__._cast(_5313.WormGearSetModalAnalysisAtAStiffness)

    @property
    def zerol_bevel_gear_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5315.ZerolBevelGearModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5315,
        )

        return self.__parent__._cast(_5315.ZerolBevelGearModalAnalysisAtAStiffness)

    @property
    def zerol_bevel_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5316.ZerolBevelGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5316,
        )

        return self.__parent__._cast(_5316.ZerolBevelGearSetModalAnalysisAtAStiffness)

    @property
    def abstract_assembly_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5448.AbstractAssemblyModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5448,
        )

        return self.__parent__._cast(_5448.AbstractAssemblyModalAnalysisAtASpeed)

    @property
    def abstract_shaft_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5449.AbstractShaftModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5449,
        )

        return self.__parent__._cast(_5449.AbstractShaftModalAnalysisAtASpeed)

    @property
    def abstract_shaft_or_housing_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5450.AbstractShaftOrHousingModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5450,
        )

        return self.__parent__._cast(_5450.AbstractShaftOrHousingModalAnalysisAtASpeed)

    @property
    def agma_gleason_conical_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5453.AGMAGleasonConicalGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5453,
        )

        return self.__parent__._cast(_5453.AGMAGleasonConicalGearModalAnalysisAtASpeed)

    @property
    def agma_gleason_conical_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5454.AGMAGleasonConicalGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5454,
        )

        return self.__parent__._cast(
            _5454.AGMAGleasonConicalGearSetModalAnalysisAtASpeed
        )

    @property
    def assembly_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5455.AssemblyModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5455,
        )

        return self.__parent__._cast(_5455.AssemblyModalAnalysisAtASpeed)

    @property
    def bearing_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5456.BearingModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5456,
        )

        return self.__parent__._cast(_5456.BearingModalAnalysisAtASpeed)

    @property
    def belt_drive_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5458.BeltDriveModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5458,
        )

        return self.__parent__._cast(_5458.BeltDriveModalAnalysisAtASpeed)

    @property
    def bevel_differential_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5460.BevelDifferentialGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5460,
        )

        return self.__parent__._cast(_5460.BevelDifferentialGearModalAnalysisAtASpeed)

    @property
    def bevel_differential_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5461.BevelDifferentialGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5461,
        )

        return self.__parent__._cast(
            _5461.BevelDifferentialGearSetModalAnalysisAtASpeed
        )

    @property
    def bevel_differential_planet_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5462.BevelDifferentialPlanetGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5462,
        )

        return self.__parent__._cast(
            _5462.BevelDifferentialPlanetGearModalAnalysisAtASpeed
        )

    @property
    def bevel_differential_sun_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5463.BevelDifferentialSunGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5463,
        )

        return self.__parent__._cast(
            _5463.BevelDifferentialSunGearModalAnalysisAtASpeed
        )

    @property
    def bevel_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5465.BevelGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5465,
        )

        return self.__parent__._cast(_5465.BevelGearModalAnalysisAtASpeed)

    @property
    def bevel_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5466.BevelGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5466,
        )

        return self.__parent__._cast(_5466.BevelGearSetModalAnalysisAtASpeed)

    @property
    def bolted_joint_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5467.BoltedJointModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5467,
        )

        return self.__parent__._cast(_5467.BoltedJointModalAnalysisAtASpeed)

    @property
    def bolt_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5468.BoltModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5468,
        )

        return self.__parent__._cast(_5468.BoltModalAnalysisAtASpeed)

    @property
    def clutch_half_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5470.ClutchHalfModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5470,
        )

        return self.__parent__._cast(_5470.ClutchHalfModalAnalysisAtASpeed)

    @property
    def clutch_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5471.ClutchModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5471,
        )

        return self.__parent__._cast(_5471.ClutchModalAnalysisAtASpeed)

    @property
    def component_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5473.ComponentModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5473,
        )

        return self.__parent__._cast(_5473.ComponentModalAnalysisAtASpeed)

    @property
    def concept_coupling_half_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5475.ConceptCouplingHalfModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5475,
        )

        return self.__parent__._cast(_5475.ConceptCouplingHalfModalAnalysisAtASpeed)

    @property
    def concept_coupling_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5476.ConceptCouplingModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5476,
        )

        return self.__parent__._cast(_5476.ConceptCouplingModalAnalysisAtASpeed)

    @property
    def concept_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5478.ConceptGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5478,
        )

        return self.__parent__._cast(_5478.ConceptGearModalAnalysisAtASpeed)

    @property
    def concept_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5479.ConceptGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5479,
        )

        return self.__parent__._cast(_5479.ConceptGearSetModalAnalysisAtASpeed)

    @property
    def conical_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5481.ConicalGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5481,
        )

        return self.__parent__._cast(_5481.ConicalGearModalAnalysisAtASpeed)

    @property
    def conical_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5482.ConicalGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5482,
        )

        return self.__parent__._cast(_5482.ConicalGearSetModalAnalysisAtASpeed)

    @property
    def connector_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5484.ConnectorModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5484,
        )

        return self.__parent__._cast(_5484.ConnectorModalAnalysisAtASpeed)

    @property
    def coupling_half_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5486.CouplingHalfModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5486,
        )

        return self.__parent__._cast(_5486.CouplingHalfModalAnalysisAtASpeed)

    @property
    def coupling_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5487.CouplingModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5487,
        )

        return self.__parent__._cast(_5487.CouplingModalAnalysisAtASpeed)

    @property
    def cvt_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5489.CVTModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5489,
        )

        return self.__parent__._cast(_5489.CVTModalAnalysisAtASpeed)

    @property
    def cvt_pulley_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5490.CVTPulleyModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5490,
        )

        return self.__parent__._cast(_5490.CVTPulleyModalAnalysisAtASpeed)

    @property
    def cycloidal_assembly_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5491.CycloidalAssemblyModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5491,
        )

        return self.__parent__._cast(_5491.CycloidalAssemblyModalAnalysisAtASpeed)

    @property
    def cycloidal_disc_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5493.CycloidalDiscModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5493,
        )

        return self.__parent__._cast(_5493.CycloidalDiscModalAnalysisAtASpeed)

    @property
    def cylindrical_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5496.CylindricalGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5496,
        )

        return self.__parent__._cast(_5496.CylindricalGearModalAnalysisAtASpeed)

    @property
    def cylindrical_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5497.CylindricalGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5497,
        )

        return self.__parent__._cast(_5497.CylindricalGearSetModalAnalysisAtASpeed)

    @property
    def cylindrical_planet_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5498.CylindricalPlanetGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5498,
        )

        return self.__parent__._cast(_5498.CylindricalPlanetGearModalAnalysisAtASpeed)

    @property
    def datum_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5499.DatumModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5499,
        )

        return self.__parent__._cast(_5499.DatumModalAnalysisAtASpeed)

    @property
    def external_cad_model_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5500.ExternalCADModelModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5500,
        )

        return self.__parent__._cast(_5500.ExternalCADModelModalAnalysisAtASpeed)

    @property
    def face_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5502.FaceGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5502,
        )

        return self.__parent__._cast(_5502.FaceGearModalAnalysisAtASpeed)

    @property
    def face_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5503.FaceGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5503,
        )

        return self.__parent__._cast(_5503.FaceGearSetModalAnalysisAtASpeed)

    @property
    def fe_part_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5504.FEPartModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5504,
        )

        return self.__parent__._cast(_5504.FEPartModalAnalysisAtASpeed)

    @property
    def flexible_pin_assembly_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5505.FlexiblePinAssemblyModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5505,
        )

        return self.__parent__._cast(_5505.FlexiblePinAssemblyModalAnalysisAtASpeed)

    @property
    def gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5507.GearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5507,
        )

        return self.__parent__._cast(_5507.GearModalAnalysisAtASpeed)

    @property
    def gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5508.GearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5508,
        )

        return self.__parent__._cast(_5508.GearSetModalAnalysisAtASpeed)

    @property
    def guide_dxf_model_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5509.GuideDxfModelModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5509,
        )

        return self.__parent__._cast(_5509.GuideDxfModelModalAnalysisAtASpeed)

    @property
    def hypoid_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5511.HypoidGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5511,
        )

        return self.__parent__._cast(_5511.HypoidGearModalAnalysisAtASpeed)

    @property
    def hypoid_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5512.HypoidGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5512,
        )

        return self.__parent__._cast(_5512.HypoidGearSetModalAnalysisAtASpeed)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5515.KlingelnbergCycloPalloidConicalGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5515,
        )

        return self.__parent__._cast(
            _5515.KlingelnbergCycloPalloidConicalGearModalAnalysisAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5516.KlingelnbergCycloPalloidConicalGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5516,
        )

        return self.__parent__._cast(
            _5516.KlingelnbergCycloPalloidConicalGearSetModalAnalysisAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5518.KlingelnbergCycloPalloidHypoidGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5518,
        )

        return self.__parent__._cast(
            _5518.KlingelnbergCycloPalloidHypoidGearModalAnalysisAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5519.KlingelnbergCycloPalloidHypoidGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5519,
        )

        return self.__parent__._cast(
            _5519.KlingelnbergCycloPalloidHypoidGearSetModalAnalysisAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5521.KlingelnbergCycloPalloidSpiralBevelGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5521,
        )

        return self.__parent__._cast(
            _5521.KlingelnbergCycloPalloidSpiralBevelGearModalAnalysisAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5522.KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5522,
        )

        return self.__parent__._cast(
            _5522.KlingelnbergCycloPalloidSpiralBevelGearSetModalAnalysisAtASpeed
        )

    @property
    def mass_disc_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5523.MassDiscModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5523,
        )

        return self.__parent__._cast(_5523.MassDiscModalAnalysisAtASpeed)

    @property
    def measurement_component_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5524.MeasurementComponentModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5524,
        )

        return self.__parent__._cast(_5524.MeasurementComponentModalAnalysisAtASpeed)

    @property
    def microphone_array_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5525.MicrophoneArrayModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5525,
        )

        return self.__parent__._cast(_5525.MicrophoneArrayModalAnalysisAtASpeed)

    @property
    def microphone_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5526.MicrophoneModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5526,
        )

        return self.__parent__._cast(_5526.MicrophoneModalAnalysisAtASpeed)

    @property
    def mountable_component_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5528.MountableComponentModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5528,
        )

        return self.__parent__._cast(_5528.MountableComponentModalAnalysisAtASpeed)

    @property
    def oil_seal_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5529.OilSealModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5529,
        )

        return self.__parent__._cast(_5529.OilSealModalAnalysisAtASpeed)

    @property
    def part_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5530.PartModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5530,
        )

        return self.__parent__._cast(_5530.PartModalAnalysisAtASpeed)

    @property
    def part_to_part_shear_coupling_half_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5532.PartToPartShearCouplingHalfModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5532,
        )

        return self.__parent__._cast(
            _5532.PartToPartShearCouplingHalfModalAnalysisAtASpeed
        )

    @property
    def part_to_part_shear_coupling_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5533.PartToPartShearCouplingModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5533,
        )

        return self.__parent__._cast(_5533.PartToPartShearCouplingModalAnalysisAtASpeed)

    @property
    def planetary_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5535.PlanetaryGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5535,
        )

        return self.__parent__._cast(_5535.PlanetaryGearSetModalAnalysisAtASpeed)

    @property
    def planet_carrier_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5536.PlanetCarrierModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5536,
        )

        return self.__parent__._cast(_5536.PlanetCarrierModalAnalysisAtASpeed)

    @property
    def point_load_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5537.PointLoadModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5537,
        )

        return self.__parent__._cast(_5537.PointLoadModalAnalysisAtASpeed)

    @property
    def power_load_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5538.PowerLoadModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5538,
        )

        return self.__parent__._cast(_5538.PowerLoadModalAnalysisAtASpeed)

    @property
    def pulley_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5539.PulleyModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5539,
        )

        return self.__parent__._cast(_5539.PulleyModalAnalysisAtASpeed)

    @property
    def ring_pins_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5540.RingPinsModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5540,
        )

        return self.__parent__._cast(_5540.RingPinsModalAnalysisAtASpeed)

    @property
    def rolling_ring_assembly_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5542.RollingRingAssemblyModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5542,
        )

        return self.__parent__._cast(_5542.RollingRingAssemblyModalAnalysisAtASpeed)

    @property
    def rolling_ring_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5544.RollingRingModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5544,
        )

        return self.__parent__._cast(_5544.RollingRingModalAnalysisAtASpeed)

    @property
    def root_assembly_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5545.RootAssemblyModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5545,
        )

        return self.__parent__._cast(_5545.RootAssemblyModalAnalysisAtASpeed)

    @property
    def shaft_hub_connection_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5546.ShaftHubConnectionModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5546,
        )

        return self.__parent__._cast(_5546.ShaftHubConnectionModalAnalysisAtASpeed)

    @property
    def shaft_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5547.ShaftModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5547,
        )

        return self.__parent__._cast(_5547.ShaftModalAnalysisAtASpeed)

    @property
    def specialised_assembly_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5549.SpecialisedAssemblyModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5549,
        )

        return self.__parent__._cast(_5549.SpecialisedAssemblyModalAnalysisAtASpeed)

    @property
    def spiral_bevel_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5551.SpiralBevelGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5551,
        )

        return self.__parent__._cast(_5551.SpiralBevelGearModalAnalysisAtASpeed)

    @property
    def spiral_bevel_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5552.SpiralBevelGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5552,
        )

        return self.__parent__._cast(_5552.SpiralBevelGearSetModalAnalysisAtASpeed)

    @property
    def spring_damper_half_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5554.SpringDamperHalfModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5554,
        )

        return self.__parent__._cast(_5554.SpringDamperHalfModalAnalysisAtASpeed)

    @property
    def spring_damper_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5555.SpringDamperModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5555,
        )

        return self.__parent__._cast(_5555.SpringDamperModalAnalysisAtASpeed)

    @property
    def straight_bevel_diff_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5557.StraightBevelDiffGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5557,
        )

        return self.__parent__._cast(_5557.StraightBevelDiffGearModalAnalysisAtASpeed)

    @property
    def straight_bevel_diff_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5558.StraightBevelDiffGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5558,
        )

        return self.__parent__._cast(
            _5558.StraightBevelDiffGearSetModalAnalysisAtASpeed
        )

    @property
    def straight_bevel_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5560.StraightBevelGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5560,
        )

        return self.__parent__._cast(_5560.StraightBevelGearModalAnalysisAtASpeed)

    @property
    def straight_bevel_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5561.StraightBevelGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5561,
        )

        return self.__parent__._cast(_5561.StraightBevelGearSetModalAnalysisAtASpeed)

    @property
    def straight_bevel_planet_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5562.StraightBevelPlanetGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5562,
        )

        return self.__parent__._cast(_5562.StraightBevelPlanetGearModalAnalysisAtASpeed)

    @property
    def straight_bevel_sun_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5563.StraightBevelSunGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5563,
        )

        return self.__parent__._cast(_5563.StraightBevelSunGearModalAnalysisAtASpeed)

    @property
    def synchroniser_half_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5564.SynchroniserHalfModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5564,
        )

        return self.__parent__._cast(_5564.SynchroniserHalfModalAnalysisAtASpeed)

    @property
    def synchroniser_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5565.SynchroniserModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5565,
        )

        return self.__parent__._cast(_5565.SynchroniserModalAnalysisAtASpeed)

    @property
    def synchroniser_part_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5566.SynchroniserPartModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5566,
        )

        return self.__parent__._cast(_5566.SynchroniserPartModalAnalysisAtASpeed)

    @property
    def synchroniser_sleeve_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5567.SynchroniserSleeveModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5567,
        )

        return self.__parent__._cast(_5567.SynchroniserSleeveModalAnalysisAtASpeed)

    @property
    def torque_converter_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5569.TorqueConverterModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5569,
        )

        return self.__parent__._cast(_5569.TorqueConverterModalAnalysisAtASpeed)

    @property
    def torque_converter_pump_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5570.TorqueConverterPumpModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5570,
        )

        return self.__parent__._cast(_5570.TorqueConverterPumpModalAnalysisAtASpeed)

    @property
    def torque_converter_turbine_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5571.TorqueConverterTurbineModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5571,
        )

        return self.__parent__._cast(_5571.TorqueConverterTurbineModalAnalysisAtASpeed)

    @property
    def unbalanced_mass_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5572.UnbalancedMassModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5572,
        )

        return self.__parent__._cast(_5572.UnbalancedMassModalAnalysisAtASpeed)

    @property
    def virtual_component_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5573.VirtualComponentModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5573,
        )

        return self.__parent__._cast(_5573.VirtualComponentModalAnalysisAtASpeed)

    @property
    def worm_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5575.WormGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5575,
        )

        return self.__parent__._cast(_5575.WormGearModalAnalysisAtASpeed)

    @property
    def worm_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5576.WormGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5576,
        )

        return self.__parent__._cast(_5576.WormGearSetModalAnalysisAtASpeed)

    @property
    def zerol_bevel_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5578.ZerolBevelGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5578,
        )

        return self.__parent__._cast(_5578.ZerolBevelGearModalAnalysisAtASpeed)

    @property
    def zerol_bevel_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5579.ZerolBevelGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5579,
        )

        return self.__parent__._cast(_5579.ZerolBevelGearSetModalAnalysisAtASpeed)

    @property
    def abstract_assembly_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5711.AbstractAssemblyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5711,
        )

        return self.__parent__._cast(_5711.AbstractAssemblyMultibodyDynamicsAnalysis)

    @property
    def abstract_shaft_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5712.AbstractShaftMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5712,
        )

        return self.__parent__._cast(_5712.AbstractShaftMultibodyDynamicsAnalysis)

    @property
    def abstract_shaft_or_housing_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5713.AbstractShaftOrHousingMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5713,
        )

        return self.__parent__._cast(
            _5713.AbstractShaftOrHousingMultibodyDynamicsAnalysis
        )

    @property
    def agma_gleason_conical_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5716.AGMAGleasonConicalGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5716,
        )

        return self.__parent__._cast(
            _5716.AGMAGleasonConicalGearMultibodyDynamicsAnalysis
        )

    @property
    def agma_gleason_conical_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5717.AGMAGleasonConicalGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5717,
        )

        return self.__parent__._cast(
            _5717.AGMAGleasonConicalGearSetMultibodyDynamicsAnalysis
        )

    @property
    def assembly_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5719.AssemblyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5719,
        )

        return self.__parent__._cast(_5719.AssemblyMultibodyDynamicsAnalysis)

    @property
    def bearing_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5721.BearingMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5721,
        )

        return self.__parent__._cast(_5721.BearingMultibodyDynamicsAnalysis)

    @property
    def belt_drive_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5724.BeltDriveMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5724,
        )

        return self.__parent__._cast(_5724.BeltDriveMultibodyDynamicsAnalysis)

    @property
    def bevel_differential_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5726.BevelDifferentialGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5726,
        )

        return self.__parent__._cast(
            _5726.BevelDifferentialGearMultibodyDynamicsAnalysis
        )

    @property
    def bevel_differential_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5727.BevelDifferentialGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5727,
        )

        return self.__parent__._cast(
            _5727.BevelDifferentialGearSetMultibodyDynamicsAnalysis
        )

    @property
    def bevel_differential_planet_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5728.BevelDifferentialPlanetGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5728,
        )

        return self.__parent__._cast(
            _5728.BevelDifferentialPlanetGearMultibodyDynamicsAnalysis
        )

    @property
    def bevel_differential_sun_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5729.BevelDifferentialSunGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5729,
        )

        return self.__parent__._cast(
            _5729.BevelDifferentialSunGearMultibodyDynamicsAnalysis
        )

    @property
    def bevel_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5731.BevelGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5731,
        )

        return self.__parent__._cast(_5731.BevelGearMultibodyDynamicsAnalysis)

    @property
    def bevel_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5732.BevelGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5732,
        )

        return self.__parent__._cast(_5732.BevelGearSetMultibodyDynamicsAnalysis)

    @property
    def bolted_joint_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5733.BoltedJointMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5733,
        )

        return self.__parent__._cast(_5733.BoltedJointMultibodyDynamicsAnalysis)

    @property
    def bolt_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5734.BoltMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5734,
        )

        return self.__parent__._cast(_5734.BoltMultibodyDynamicsAnalysis)

    @property
    def clutch_half_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5736.ClutchHalfMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5736,
        )

        return self.__parent__._cast(_5736.ClutchHalfMultibodyDynamicsAnalysis)

    @property
    def clutch_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5737.ClutchMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5737,
        )

        return self.__parent__._cast(_5737.ClutchMultibodyDynamicsAnalysis)

    @property
    def component_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5740.ComponentMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5740,
        )

        return self.__parent__._cast(_5740.ComponentMultibodyDynamicsAnalysis)

    @property
    def concept_coupling_half_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5742.ConceptCouplingHalfMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5742,
        )

        return self.__parent__._cast(_5742.ConceptCouplingHalfMultibodyDynamicsAnalysis)

    @property
    def concept_coupling_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5743.ConceptCouplingMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5743,
        )

        return self.__parent__._cast(_5743.ConceptCouplingMultibodyDynamicsAnalysis)

    @property
    def concept_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5745.ConceptGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5745,
        )

        return self.__parent__._cast(_5745.ConceptGearMultibodyDynamicsAnalysis)

    @property
    def concept_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5746.ConceptGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5746,
        )

        return self.__parent__._cast(_5746.ConceptGearSetMultibodyDynamicsAnalysis)

    @property
    def conical_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5748.ConicalGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5748,
        )

        return self.__parent__._cast(_5748.ConicalGearMultibodyDynamicsAnalysis)

    @property
    def conical_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5749.ConicalGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5749,
        )

        return self.__parent__._cast(_5749.ConicalGearSetMultibodyDynamicsAnalysis)

    @property
    def connector_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5751.ConnectorMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5751,
        )

        return self.__parent__._cast(_5751.ConnectorMultibodyDynamicsAnalysis)

    @property
    def coupling_half_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5753.CouplingHalfMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5753,
        )

        return self.__parent__._cast(_5753.CouplingHalfMultibodyDynamicsAnalysis)

    @property
    def coupling_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5754.CouplingMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5754,
        )

        return self.__parent__._cast(_5754.CouplingMultibodyDynamicsAnalysis)

    @property
    def cvt_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5756.CVTMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5756,
        )

        return self.__parent__._cast(_5756.CVTMultibodyDynamicsAnalysis)

    @property
    def cvt_pulley_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5757.CVTPulleyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5757,
        )

        return self.__parent__._cast(_5757.CVTPulleyMultibodyDynamicsAnalysis)

    @property
    def cycloidal_assembly_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5758.CycloidalAssemblyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5758,
        )

        return self.__parent__._cast(_5758.CycloidalAssemblyMultibodyDynamicsAnalysis)

    @property
    def cycloidal_disc_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5760.CycloidalDiscMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5760,
        )

        return self.__parent__._cast(_5760.CycloidalDiscMultibodyDynamicsAnalysis)

    @property
    def cylindrical_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5763.CylindricalGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5763,
        )

        return self.__parent__._cast(_5763.CylindricalGearMultibodyDynamicsAnalysis)

    @property
    def cylindrical_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5764.CylindricalGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5764,
        )

        return self.__parent__._cast(_5764.CylindricalGearSetMultibodyDynamicsAnalysis)

    @property
    def cylindrical_planet_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5765.CylindricalPlanetGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5765,
        )

        return self.__parent__._cast(
            _5765.CylindricalPlanetGearMultibodyDynamicsAnalysis
        )

    @property
    def datum_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5766.DatumMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5766,
        )

        return self.__parent__._cast(_5766.DatumMultibodyDynamicsAnalysis)

    @property
    def external_cad_model_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5767.ExternalCADModelMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5767,
        )

        return self.__parent__._cast(_5767.ExternalCADModelMultibodyDynamicsAnalysis)

    @property
    def face_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5769.FaceGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5769,
        )

        return self.__parent__._cast(_5769.FaceGearMultibodyDynamicsAnalysis)

    @property
    def face_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5770.FaceGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5770,
        )

        return self.__parent__._cast(_5770.FaceGearSetMultibodyDynamicsAnalysis)

    @property
    def fe_part_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5771.FEPartMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5771,
        )

        return self.__parent__._cast(_5771.FEPartMultibodyDynamicsAnalysis)

    @property
    def flexible_pin_assembly_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5772.FlexiblePinAssemblyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5772,
        )

        return self.__parent__._cast(_5772.FlexiblePinAssemblyMultibodyDynamicsAnalysis)

    @property
    def gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5775.GearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5775,
        )

        return self.__parent__._cast(_5775.GearMultibodyDynamicsAnalysis)

    @property
    def gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5776.GearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5776,
        )

        return self.__parent__._cast(_5776.GearSetMultibodyDynamicsAnalysis)

    @property
    def guide_dxf_model_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5777.GuideDxfModelMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5777,
        )

        return self.__parent__._cast(_5777.GuideDxfModelMultibodyDynamicsAnalysis)

    @property
    def hypoid_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5779.HypoidGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5779,
        )

        return self.__parent__._cast(_5779.HypoidGearMultibodyDynamicsAnalysis)

    @property
    def hypoid_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5780.HypoidGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5780,
        )

        return self.__parent__._cast(_5780.HypoidGearSetMultibodyDynamicsAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5787.KlingelnbergCycloPalloidConicalGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5787,
        )

        return self.__parent__._cast(
            _5787.KlingelnbergCycloPalloidConicalGearMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5788.KlingelnbergCycloPalloidConicalGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5788,
        )

        return self.__parent__._cast(
            _5788.KlingelnbergCycloPalloidConicalGearSetMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5790.KlingelnbergCycloPalloidHypoidGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5790,
        )

        return self.__parent__._cast(
            _5790.KlingelnbergCycloPalloidHypoidGearMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5791.KlingelnbergCycloPalloidHypoidGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5791,
        )

        return self.__parent__._cast(
            _5791.KlingelnbergCycloPalloidHypoidGearSetMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5793.KlingelnbergCycloPalloidSpiralBevelGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5793,
        )

        return self.__parent__._cast(
            _5793.KlingelnbergCycloPalloidSpiralBevelGearMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5794.KlingelnbergCycloPalloidSpiralBevelGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5794,
        )

        return self.__parent__._cast(
            _5794.KlingelnbergCycloPalloidSpiralBevelGearSetMultibodyDynamicsAnalysis
        )

    @property
    def mass_disc_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5795.MassDiscMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5795,
        )

        return self.__parent__._cast(_5795.MassDiscMultibodyDynamicsAnalysis)

    @property
    def measurement_component_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5799.MeasurementComponentMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5799,
        )

        return self.__parent__._cast(
            _5799.MeasurementComponentMultibodyDynamicsAnalysis
        )

    @property
    def microphone_array_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5800.MicrophoneArrayMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5800,
        )

        return self.__parent__._cast(_5800.MicrophoneArrayMultibodyDynamicsAnalysis)

    @property
    def microphone_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5801.MicrophoneMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5801,
        )

        return self.__parent__._cast(_5801.MicrophoneMultibodyDynamicsAnalysis)

    @property
    def mountable_component_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5802.MountableComponentMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5802,
        )

        return self.__parent__._cast(_5802.MountableComponentMultibodyDynamicsAnalysis)

    @property
    def oil_seal_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5804.OilSealMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5804,
        )

        return self.__parent__._cast(_5804.OilSealMultibodyDynamicsAnalysis)

    @property
    def part_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5805.PartMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5805,
        )

        return self.__parent__._cast(_5805.PartMultibodyDynamicsAnalysis)

    @property
    def part_to_part_shear_coupling_half_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5807.PartToPartShearCouplingHalfMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5807,
        )

        return self.__parent__._cast(
            _5807.PartToPartShearCouplingHalfMultibodyDynamicsAnalysis
        )

    @property
    def part_to_part_shear_coupling_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5808.PartToPartShearCouplingMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5808,
        )

        return self.__parent__._cast(
            _5808.PartToPartShearCouplingMultibodyDynamicsAnalysis
        )

    @property
    def planetary_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5810.PlanetaryGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5810,
        )

        return self.__parent__._cast(_5810.PlanetaryGearSetMultibodyDynamicsAnalysis)

    @property
    def planet_carrier_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5811.PlanetCarrierMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5811,
        )

        return self.__parent__._cast(_5811.PlanetCarrierMultibodyDynamicsAnalysis)

    @property
    def point_load_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5812.PointLoadMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5812,
        )

        return self.__parent__._cast(_5812.PointLoadMultibodyDynamicsAnalysis)

    @property
    def power_load_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5813.PowerLoadMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5813,
        )

        return self.__parent__._cast(_5813.PowerLoadMultibodyDynamicsAnalysis)

    @property
    def pulley_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5814.PulleyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5814,
        )

        return self.__parent__._cast(_5814.PulleyMultibodyDynamicsAnalysis)

    @property
    def ring_pins_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5815.RingPinsMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5815,
        )

        return self.__parent__._cast(_5815.RingPinsMultibodyDynamicsAnalysis)

    @property
    def rolling_ring_assembly_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5817.RollingRingAssemblyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5817,
        )

        return self.__parent__._cast(_5817.RollingRingAssemblyMultibodyDynamicsAnalysis)

    @property
    def rolling_ring_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5819.RollingRingMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5819,
        )

        return self.__parent__._cast(_5819.RollingRingMultibodyDynamicsAnalysis)

    @property
    def root_assembly_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5820.RootAssemblyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5820,
        )

        return self.__parent__._cast(_5820.RootAssemblyMultibodyDynamicsAnalysis)

    @property
    def shaft_hub_connection_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5823.ShaftHubConnectionMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5823,
        )

        return self.__parent__._cast(_5823.ShaftHubConnectionMultibodyDynamicsAnalysis)

    @property
    def shaft_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5824.ShaftMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5824,
        )

        return self.__parent__._cast(_5824.ShaftMultibodyDynamicsAnalysis)

    @property
    def specialised_assembly_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5827.SpecialisedAssemblyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5827,
        )

        return self.__parent__._cast(_5827.SpecialisedAssemblyMultibodyDynamicsAnalysis)

    @property
    def spiral_bevel_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5829.SpiralBevelGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5829,
        )

        return self.__parent__._cast(_5829.SpiralBevelGearMultibodyDynamicsAnalysis)

    @property
    def spiral_bevel_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5830.SpiralBevelGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5830,
        )

        return self.__parent__._cast(_5830.SpiralBevelGearSetMultibodyDynamicsAnalysis)

    @property
    def spring_damper_half_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5833.SpringDamperHalfMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5833,
        )

        return self.__parent__._cast(_5833.SpringDamperHalfMultibodyDynamicsAnalysis)

    @property
    def spring_damper_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5834.SpringDamperMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5834,
        )

        return self.__parent__._cast(_5834.SpringDamperMultibodyDynamicsAnalysis)

    @property
    def straight_bevel_diff_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5836.StraightBevelDiffGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5836,
        )

        return self.__parent__._cast(
            _5836.StraightBevelDiffGearMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_diff_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5837.StraightBevelDiffGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5837,
        )

        return self.__parent__._cast(
            _5837.StraightBevelDiffGearSetMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5839.StraightBevelGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5839,
        )

        return self.__parent__._cast(_5839.StraightBevelGearMultibodyDynamicsAnalysis)

    @property
    def straight_bevel_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5840.StraightBevelGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5840,
        )

        return self.__parent__._cast(
            _5840.StraightBevelGearSetMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_planet_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5841.StraightBevelPlanetGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5841,
        )

        return self.__parent__._cast(
            _5841.StraightBevelPlanetGearMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_sun_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5842.StraightBevelSunGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5842,
        )

        return self.__parent__._cast(
            _5842.StraightBevelSunGearMultibodyDynamicsAnalysis
        )

    @property
    def synchroniser_half_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5843.SynchroniserHalfMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5843,
        )

        return self.__parent__._cast(_5843.SynchroniserHalfMultibodyDynamicsAnalysis)

    @property
    def synchroniser_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5844.SynchroniserMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5844,
        )

        return self.__parent__._cast(_5844.SynchroniserMultibodyDynamicsAnalysis)

    @property
    def synchroniser_part_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5845.SynchroniserPartMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5845,
        )

        return self.__parent__._cast(_5845.SynchroniserPartMultibodyDynamicsAnalysis)

    @property
    def synchroniser_sleeve_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5846.SynchroniserSleeveMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5846,
        )

        return self.__parent__._cast(_5846.SynchroniserSleeveMultibodyDynamicsAnalysis)

    @property
    def torque_converter_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5849.TorqueConverterMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5849,
        )

        return self.__parent__._cast(_5849.TorqueConverterMultibodyDynamicsAnalysis)

    @property
    def torque_converter_pump_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5850.TorqueConverterPumpMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5850,
        )

        return self.__parent__._cast(_5850.TorqueConverterPumpMultibodyDynamicsAnalysis)

    @property
    def torque_converter_turbine_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5852.TorqueConverterTurbineMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5852,
        )

        return self.__parent__._cast(
            _5852.TorqueConverterTurbineMultibodyDynamicsAnalysis
        )

    @property
    def unbalanced_mass_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5853.UnbalancedMassMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5853,
        )

        return self.__parent__._cast(_5853.UnbalancedMassMultibodyDynamicsAnalysis)

    @property
    def virtual_component_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5854.VirtualComponentMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5854,
        )

        return self.__parent__._cast(_5854.VirtualComponentMultibodyDynamicsAnalysis)

    @property
    def worm_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5857.WormGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5857,
        )

        return self.__parent__._cast(_5857.WormGearMultibodyDynamicsAnalysis)

    @property
    def worm_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5858.WormGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5858,
        )

        return self.__parent__._cast(_5858.WormGearSetMultibodyDynamicsAnalysis)

    @property
    def zerol_bevel_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5860.ZerolBevelGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5860,
        )

        return self.__parent__._cast(_5860.ZerolBevelGearMultibodyDynamicsAnalysis)

    @property
    def zerol_bevel_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5861.ZerolBevelGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5861,
        )

        return self.__parent__._cast(_5861.ZerolBevelGearSetMultibodyDynamicsAnalysis)

    @property
    def abstract_assembly_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6020.AbstractAssemblyHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6020,
        )

        return self.__parent__._cast(_6020.AbstractAssemblyHarmonicAnalysis)

    @property
    def abstract_shaft_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6022.AbstractShaftHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6022,
        )

        return self.__parent__._cast(_6022.AbstractShaftHarmonicAnalysis)

    @property
    def abstract_shaft_or_housing_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6023.AbstractShaftOrHousingHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6023,
        )

        return self.__parent__._cast(_6023.AbstractShaftOrHousingHarmonicAnalysis)

    @property
    def agma_gleason_conical_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6025.AGMAGleasonConicalGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6025,
        )

        return self.__parent__._cast(_6025.AGMAGleasonConicalGearHarmonicAnalysis)

    @property
    def agma_gleason_conical_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6027.AGMAGleasonConicalGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6027,
        )

        return self.__parent__._cast(_6027.AGMAGleasonConicalGearSetHarmonicAnalysis)

    @property
    def assembly_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6028.AssemblyHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6028,
        )

        return self.__parent__._cast(_6028.AssemblyHarmonicAnalysis)

    @property
    def bearing_harmonic_analysis(self: "CastSelf") -> "_6029.BearingHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6029,
        )

        return self.__parent__._cast(_6029.BearingHarmonicAnalysis)

    @property
    def belt_drive_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6031.BeltDriveHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6031,
        )

        return self.__parent__._cast(_6031.BeltDriveHarmonicAnalysis)

    @property
    def bevel_differential_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6032.BevelDifferentialGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6032,
        )

        return self.__parent__._cast(_6032.BevelDifferentialGearHarmonicAnalysis)

    @property
    def bevel_differential_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6034.BevelDifferentialGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6034,
        )

        return self.__parent__._cast(_6034.BevelDifferentialGearSetHarmonicAnalysis)

    @property
    def bevel_differential_planet_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6035.BevelDifferentialPlanetGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6035,
        )

        return self.__parent__._cast(_6035.BevelDifferentialPlanetGearHarmonicAnalysis)

    @property
    def bevel_differential_sun_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6036.BevelDifferentialSunGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6036,
        )

        return self.__parent__._cast(_6036.BevelDifferentialSunGearHarmonicAnalysis)

    @property
    def bevel_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6037.BevelGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6037,
        )

        return self.__parent__._cast(_6037.BevelGearHarmonicAnalysis)

    @property
    def bevel_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6039.BevelGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6039,
        )

        return self.__parent__._cast(_6039.BevelGearSetHarmonicAnalysis)

    @property
    def bolted_joint_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6040.BoltedJointHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6040,
        )

        return self.__parent__._cast(_6040.BoltedJointHarmonicAnalysis)

    @property
    def bolt_harmonic_analysis(self: "CastSelf") -> "_6041.BoltHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6041,
        )

        return self.__parent__._cast(_6041.BoltHarmonicAnalysis)

    @property
    def clutch_half_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6043.ClutchHalfHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6043,
        )

        return self.__parent__._cast(_6043.ClutchHalfHarmonicAnalysis)

    @property
    def clutch_harmonic_analysis(self: "CastSelf") -> "_6044.ClutchHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6044,
        )

        return self.__parent__._cast(_6044.ClutchHarmonicAnalysis)

    @property
    def component_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6047.ComponentHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6047,
        )

        return self.__parent__._cast(_6047.ComponentHarmonicAnalysis)

    @property
    def concept_coupling_half_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6049.ConceptCouplingHalfHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6049,
        )

        return self.__parent__._cast(_6049.ConceptCouplingHalfHarmonicAnalysis)

    @property
    def concept_coupling_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6050.ConceptCouplingHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6050,
        )

        return self.__parent__._cast(_6050.ConceptCouplingHarmonicAnalysis)

    @property
    def concept_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6051.ConceptGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6051,
        )

        return self.__parent__._cast(_6051.ConceptGearHarmonicAnalysis)

    @property
    def concept_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6053.ConceptGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6053,
        )

        return self.__parent__._cast(_6053.ConceptGearSetHarmonicAnalysis)

    @property
    def conical_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6054.ConicalGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6054,
        )

        return self.__parent__._cast(_6054.ConicalGearHarmonicAnalysis)

    @property
    def conical_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6056.ConicalGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6056,
        )

        return self.__parent__._cast(_6056.ConicalGearSetHarmonicAnalysis)

    @property
    def connector_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6058.ConnectorHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6058,
        )

        return self.__parent__._cast(_6058.ConnectorHarmonicAnalysis)

    @property
    def coupling_half_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6060.CouplingHalfHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6060,
        )

        return self.__parent__._cast(_6060.CouplingHalfHarmonicAnalysis)

    @property
    def coupling_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6061.CouplingHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6061,
        )

        return self.__parent__._cast(_6061.CouplingHarmonicAnalysis)

    @property
    def cvt_harmonic_analysis(self: "CastSelf") -> "_6063.CVTHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6063,
        )

        return self.__parent__._cast(_6063.CVTHarmonicAnalysis)

    @property
    def cvt_pulley_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6064.CVTPulleyHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6064,
        )

        return self.__parent__._cast(_6064.CVTPulleyHarmonicAnalysis)

    @property
    def cycloidal_assembly_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6065.CycloidalAssemblyHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6065,
        )

        return self.__parent__._cast(_6065.CycloidalAssemblyHarmonicAnalysis)

    @property
    def cycloidal_disc_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6067.CycloidalDiscHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6067,
        )

        return self.__parent__._cast(_6067.CycloidalDiscHarmonicAnalysis)

    @property
    def cylindrical_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6069.CylindricalGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6069,
        )

        return self.__parent__._cast(_6069.CylindricalGearHarmonicAnalysis)

    @property
    def cylindrical_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6071.CylindricalGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6071,
        )

        return self.__parent__._cast(_6071.CylindricalGearSetHarmonicAnalysis)

    @property
    def cylindrical_planet_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6072.CylindricalPlanetGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6072,
        )

        return self.__parent__._cast(_6072.CylindricalPlanetGearHarmonicAnalysis)

    @property
    def datum_harmonic_analysis(self: "CastSelf") -> "_6074.DatumHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6074,
        )

        return self.__parent__._cast(_6074.DatumHarmonicAnalysis)

    @property
    def external_cad_model_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6089.ExternalCADModelHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6089,
        )

        return self.__parent__._cast(_6089.ExternalCADModelHarmonicAnalysis)

    @property
    def face_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6090.FaceGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6090,
        )

        return self.__parent__._cast(_6090.FaceGearHarmonicAnalysis)

    @property
    def face_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6092.FaceGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6092,
        )

        return self.__parent__._cast(_6092.FaceGearSetHarmonicAnalysis)

    @property
    def fe_part_harmonic_analysis(self: "CastSelf") -> "_6093.FEPartHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6093,
        )

        return self.__parent__._cast(_6093.FEPartHarmonicAnalysis)

    @property
    def flexible_pin_assembly_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6094.FlexiblePinAssemblyHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6094,
        )

        return self.__parent__._cast(_6094.FlexiblePinAssemblyHarmonicAnalysis)

    @property
    def gear_harmonic_analysis(self: "CastSelf") -> "_6096.GearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6096,
        )

        return self.__parent__._cast(_6096.GearHarmonicAnalysis)

    @property
    def gear_set_harmonic_analysis(self: "CastSelf") -> "_6101.GearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6101,
        )

        return self.__parent__._cast(_6101.GearSetHarmonicAnalysis)

    @property
    def guide_dxf_model_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6103.GuideDxfModelHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6103,
        )

        return self.__parent__._cast(_6103.GuideDxfModelHarmonicAnalysis)

    @property
    def hypoid_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6116.HypoidGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6116,
        )

        return self.__parent__._cast(_6116.HypoidGearHarmonicAnalysis)

    @property
    def hypoid_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6118.HypoidGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6118,
        )

        return self.__parent__._cast(_6118.HypoidGearSetHarmonicAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6120.KlingelnbergCycloPalloidConicalGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6120,
        )

        return self.__parent__._cast(
            _6120.KlingelnbergCycloPalloidConicalGearHarmonicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6122.KlingelnbergCycloPalloidConicalGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6122,
        )

        return self.__parent__._cast(
            _6122.KlingelnbergCycloPalloidConicalGearSetHarmonicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6123.KlingelnbergCycloPalloidHypoidGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6123,
        )

        return self.__parent__._cast(
            _6123.KlingelnbergCycloPalloidHypoidGearHarmonicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6125.KlingelnbergCycloPalloidHypoidGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6125,
        )

        return self.__parent__._cast(
            _6125.KlingelnbergCycloPalloidHypoidGearSetHarmonicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6126.KlingelnbergCycloPalloidSpiralBevelGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6126,
        )

        return self.__parent__._cast(
            _6126.KlingelnbergCycloPalloidSpiralBevelGearHarmonicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6128.KlingelnbergCycloPalloidSpiralBevelGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6128,
        )

        return self.__parent__._cast(
            _6128.KlingelnbergCycloPalloidSpiralBevelGearSetHarmonicAnalysis
        )

    @property
    def mass_disc_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6129.MassDiscHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6129,
        )

        return self.__parent__._cast(_6129.MassDiscHarmonicAnalysis)

    @property
    def measurement_component_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6130.MeasurementComponentHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6130,
        )

        return self.__parent__._cast(_6130.MeasurementComponentHarmonicAnalysis)

    @property
    def microphone_array_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6131.MicrophoneArrayHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6131,
        )

        return self.__parent__._cast(_6131.MicrophoneArrayHarmonicAnalysis)

    @property
    def microphone_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6132.MicrophoneHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6132,
        )

        return self.__parent__._cast(_6132.MicrophoneHarmonicAnalysis)

    @property
    def mountable_component_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6134.MountableComponentHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6134,
        )

        return self.__parent__._cast(_6134.MountableComponentHarmonicAnalysis)

    @property
    def oil_seal_harmonic_analysis(self: "CastSelf") -> "_6135.OilSealHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6135,
        )

        return self.__parent__._cast(_6135.OilSealHarmonicAnalysis)

    @property
    def part_harmonic_analysis(self: "CastSelf") -> "_6136.PartHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6136,
        )

        return self.__parent__._cast(_6136.PartHarmonicAnalysis)

    @property
    def part_to_part_shear_coupling_half_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6138.PartToPartShearCouplingHalfHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6138,
        )

        return self.__parent__._cast(_6138.PartToPartShearCouplingHalfHarmonicAnalysis)

    @property
    def part_to_part_shear_coupling_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6139.PartToPartShearCouplingHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6139,
        )

        return self.__parent__._cast(_6139.PartToPartShearCouplingHarmonicAnalysis)

    @property
    def planetary_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6142.PlanetaryGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6142,
        )

        return self.__parent__._cast(_6142.PlanetaryGearSetHarmonicAnalysis)

    @property
    def planet_carrier_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6143.PlanetCarrierHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6143,
        )

        return self.__parent__._cast(_6143.PlanetCarrierHarmonicAnalysis)

    @property
    def point_load_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6144.PointLoadHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6144,
        )

        return self.__parent__._cast(_6144.PointLoadHarmonicAnalysis)

    @property
    def power_load_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6145.PowerLoadHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6145,
        )

        return self.__parent__._cast(_6145.PowerLoadHarmonicAnalysis)

    @property
    def pulley_harmonic_analysis(self: "CastSelf") -> "_6146.PulleyHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6146,
        )

        return self.__parent__._cast(_6146.PulleyHarmonicAnalysis)

    @property
    def ring_pins_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6148.RingPinsHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6148,
        )

        return self.__parent__._cast(_6148.RingPinsHarmonicAnalysis)

    @property
    def rolling_ring_assembly_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6150.RollingRingAssemblyHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6150,
        )

        return self.__parent__._cast(_6150.RollingRingAssemblyHarmonicAnalysis)

    @property
    def rolling_ring_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6152.RollingRingHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6152,
        )

        return self.__parent__._cast(_6152.RollingRingHarmonicAnalysis)

    @property
    def root_assembly_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6153.RootAssemblyHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6153,
        )

        return self.__parent__._cast(_6153.RootAssemblyHarmonicAnalysis)

    @property
    def shaft_harmonic_analysis(self: "CastSelf") -> "_6154.ShaftHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6154,
        )

        return self.__parent__._cast(_6154.ShaftHarmonicAnalysis)

    @property
    def shaft_hub_connection_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6155.ShaftHubConnectionHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6155,
        )

        return self.__parent__._cast(_6155.ShaftHubConnectionHarmonicAnalysis)

    @property
    def specialised_assembly_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6158.SpecialisedAssemblyHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6158,
        )

        return self.__parent__._cast(_6158.SpecialisedAssemblyHarmonicAnalysis)

    @property
    def spiral_bevel_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6160.SpiralBevelGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6160,
        )

        return self.__parent__._cast(_6160.SpiralBevelGearHarmonicAnalysis)

    @property
    def spiral_bevel_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6162.SpiralBevelGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6162,
        )

        return self.__parent__._cast(_6162.SpiralBevelGearSetHarmonicAnalysis)

    @property
    def spring_damper_half_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6164.SpringDamperHalfHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6164,
        )

        return self.__parent__._cast(_6164.SpringDamperHalfHarmonicAnalysis)

    @property
    def spring_damper_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6165.SpringDamperHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6165,
        )

        return self.__parent__._cast(_6165.SpringDamperHarmonicAnalysis)

    @property
    def straight_bevel_diff_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6167.StraightBevelDiffGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6167,
        )

        return self.__parent__._cast(_6167.StraightBevelDiffGearHarmonicAnalysis)

    @property
    def straight_bevel_diff_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6169.StraightBevelDiffGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6169,
        )

        return self.__parent__._cast(_6169.StraightBevelDiffGearSetHarmonicAnalysis)

    @property
    def straight_bevel_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6170.StraightBevelGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6170,
        )

        return self.__parent__._cast(_6170.StraightBevelGearHarmonicAnalysis)

    @property
    def straight_bevel_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6172.StraightBevelGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6172,
        )

        return self.__parent__._cast(_6172.StraightBevelGearSetHarmonicAnalysis)

    @property
    def straight_bevel_planet_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6173.StraightBevelPlanetGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6173,
        )

        return self.__parent__._cast(_6173.StraightBevelPlanetGearHarmonicAnalysis)

    @property
    def straight_bevel_sun_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6174.StraightBevelSunGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6174,
        )

        return self.__parent__._cast(_6174.StraightBevelSunGearHarmonicAnalysis)

    @property
    def synchroniser_half_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6175.SynchroniserHalfHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6175,
        )

        return self.__parent__._cast(_6175.SynchroniserHalfHarmonicAnalysis)

    @property
    def synchroniser_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6176.SynchroniserHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6176,
        )

        return self.__parent__._cast(_6176.SynchroniserHarmonicAnalysis)

    @property
    def synchroniser_part_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6177.SynchroniserPartHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6177,
        )

        return self.__parent__._cast(_6177.SynchroniserPartHarmonicAnalysis)

    @property
    def synchroniser_sleeve_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6178.SynchroniserSleeveHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6178,
        )

        return self.__parent__._cast(_6178.SynchroniserSleeveHarmonicAnalysis)

    @property
    def torque_converter_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6180.TorqueConverterHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6180,
        )

        return self.__parent__._cast(_6180.TorqueConverterHarmonicAnalysis)

    @property
    def torque_converter_pump_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6181.TorqueConverterPumpHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6181,
        )

        return self.__parent__._cast(_6181.TorqueConverterPumpHarmonicAnalysis)

    @property
    def torque_converter_turbine_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6182.TorqueConverterTurbineHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6182,
        )

        return self.__parent__._cast(_6182.TorqueConverterTurbineHarmonicAnalysis)

    @property
    def unbalanced_mass_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6184.UnbalancedMassHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6184,
        )

        return self.__parent__._cast(_6184.UnbalancedMassHarmonicAnalysis)

    @property
    def virtual_component_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6185.VirtualComponentHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6185,
        )

        return self.__parent__._cast(_6185.VirtualComponentHarmonicAnalysis)

    @property
    def worm_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6186.WormGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6186,
        )

        return self.__parent__._cast(_6186.WormGearHarmonicAnalysis)

    @property
    def worm_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6188.WormGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6188,
        )

        return self.__parent__._cast(_6188.WormGearSetHarmonicAnalysis)

    @property
    def zerol_bevel_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6189.ZerolBevelGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6189,
        )

        return self.__parent__._cast(_6189.ZerolBevelGearHarmonicAnalysis)

    @property
    def zerol_bevel_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6191.ZerolBevelGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6191,
        )

        return self.__parent__._cast(_6191.ZerolBevelGearSetHarmonicAnalysis)

    @property
    def abstract_assembly_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6368.AbstractAssemblyHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6368,
        )

        return self.__parent__._cast(
            _6368.AbstractAssemblyHarmonicAnalysisOfSingleExcitation
        )

    @property
    def abstract_shaft_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6369.AbstractShaftHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6369,
        )

        return self.__parent__._cast(
            _6369.AbstractShaftHarmonicAnalysisOfSingleExcitation
        )

    @property
    def abstract_shaft_or_housing_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6370.AbstractShaftOrHousingHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6370,
        )

        return self.__parent__._cast(
            _6370.AbstractShaftOrHousingHarmonicAnalysisOfSingleExcitation
        )

    @property
    def agma_gleason_conical_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6372.AGMAGleasonConicalGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6372,
        )

        return self.__parent__._cast(
            _6372.AGMAGleasonConicalGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def agma_gleason_conical_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6374.AGMAGleasonConicalGearSetHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6374,
        )

        return self.__parent__._cast(
            _6374.AGMAGleasonConicalGearSetHarmonicAnalysisOfSingleExcitation
        )

    @property
    def assembly_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6375.AssemblyHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6375,
        )

        return self.__parent__._cast(_6375.AssemblyHarmonicAnalysisOfSingleExcitation)

    @property
    def bearing_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6376.BearingHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6376,
        )

        return self.__parent__._cast(_6376.BearingHarmonicAnalysisOfSingleExcitation)

    @property
    def belt_drive_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6378.BeltDriveHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6378,
        )

        return self.__parent__._cast(_6378.BeltDriveHarmonicAnalysisOfSingleExcitation)

    @property
    def bevel_differential_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6379.BevelDifferentialGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6379,
        )

        return self.__parent__._cast(
            _6379.BevelDifferentialGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def bevel_differential_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6381.BevelDifferentialGearSetHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6381,
        )

        return self.__parent__._cast(
            _6381.BevelDifferentialGearSetHarmonicAnalysisOfSingleExcitation
        )

    @property
    def bevel_differential_planet_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6382.BevelDifferentialPlanetGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6382,
        )

        return self.__parent__._cast(
            _6382.BevelDifferentialPlanetGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def bevel_differential_sun_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6383.BevelDifferentialSunGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6383,
        )

        return self.__parent__._cast(
            _6383.BevelDifferentialSunGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def bevel_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6384.BevelGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6384,
        )

        return self.__parent__._cast(_6384.BevelGearHarmonicAnalysisOfSingleExcitation)

    @property
    def bevel_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6386.BevelGearSetHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6386,
        )

        return self.__parent__._cast(
            _6386.BevelGearSetHarmonicAnalysisOfSingleExcitation
        )

    @property
    def bolted_joint_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6387.BoltedJointHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6387,
        )

        return self.__parent__._cast(
            _6387.BoltedJointHarmonicAnalysisOfSingleExcitation
        )

    @property
    def bolt_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6388.BoltHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6388,
        )

        return self.__parent__._cast(_6388.BoltHarmonicAnalysisOfSingleExcitation)

    @property
    def clutch_half_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6390.ClutchHalfHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6390,
        )

        return self.__parent__._cast(_6390.ClutchHalfHarmonicAnalysisOfSingleExcitation)

    @property
    def clutch_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6391.ClutchHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6391,
        )

        return self.__parent__._cast(_6391.ClutchHarmonicAnalysisOfSingleExcitation)

    @property
    def component_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6393.ComponentHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6393,
        )

        return self.__parent__._cast(_6393.ComponentHarmonicAnalysisOfSingleExcitation)

    @property
    def concept_coupling_half_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6395.ConceptCouplingHalfHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6395,
        )

        return self.__parent__._cast(
            _6395.ConceptCouplingHalfHarmonicAnalysisOfSingleExcitation
        )

    @property
    def concept_coupling_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6396.ConceptCouplingHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6396,
        )

        return self.__parent__._cast(
            _6396.ConceptCouplingHarmonicAnalysisOfSingleExcitation
        )

    @property
    def concept_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6397.ConceptGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6397,
        )

        return self.__parent__._cast(
            _6397.ConceptGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def concept_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6399.ConceptGearSetHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6399,
        )

        return self.__parent__._cast(
            _6399.ConceptGearSetHarmonicAnalysisOfSingleExcitation
        )

    @property
    def conical_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6400.ConicalGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6400,
        )

        return self.__parent__._cast(
            _6400.ConicalGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def conical_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6402.ConicalGearSetHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6402,
        )

        return self.__parent__._cast(
            _6402.ConicalGearSetHarmonicAnalysisOfSingleExcitation
        )

    @property
    def connector_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6404.ConnectorHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6404,
        )

        return self.__parent__._cast(_6404.ConnectorHarmonicAnalysisOfSingleExcitation)

    @property
    def coupling_half_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6406.CouplingHalfHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6406,
        )

        return self.__parent__._cast(
            _6406.CouplingHalfHarmonicAnalysisOfSingleExcitation
        )

    @property
    def coupling_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6407.CouplingHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6407,
        )

        return self.__parent__._cast(_6407.CouplingHarmonicAnalysisOfSingleExcitation)

    @property
    def cvt_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6409.CVTHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6409,
        )

        return self.__parent__._cast(_6409.CVTHarmonicAnalysisOfSingleExcitation)

    @property
    def cvt_pulley_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6410.CVTPulleyHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6410,
        )

        return self.__parent__._cast(_6410.CVTPulleyHarmonicAnalysisOfSingleExcitation)

    @property
    def cycloidal_assembly_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6411.CycloidalAssemblyHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6411,
        )

        return self.__parent__._cast(
            _6411.CycloidalAssemblyHarmonicAnalysisOfSingleExcitation
        )

    @property
    def cycloidal_disc_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6413.CycloidalDiscHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6413,
        )

        return self.__parent__._cast(
            _6413.CycloidalDiscHarmonicAnalysisOfSingleExcitation
        )

    @property
    def cylindrical_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6415.CylindricalGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6415,
        )

        return self.__parent__._cast(
            _6415.CylindricalGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def cylindrical_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6417.CylindricalGearSetHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6417,
        )

        return self.__parent__._cast(
            _6417.CylindricalGearSetHarmonicAnalysisOfSingleExcitation
        )

    @property
    def cylindrical_planet_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6418.CylindricalPlanetGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6418,
        )

        return self.__parent__._cast(
            _6418.CylindricalPlanetGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def datum_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6419.DatumHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6419,
        )

        return self.__parent__._cast(_6419.DatumHarmonicAnalysisOfSingleExcitation)

    @property
    def external_cad_model_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6420.ExternalCADModelHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6420,
        )

        return self.__parent__._cast(
            _6420.ExternalCADModelHarmonicAnalysisOfSingleExcitation
        )

    @property
    def face_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6421.FaceGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6421,
        )

        return self.__parent__._cast(_6421.FaceGearHarmonicAnalysisOfSingleExcitation)

    @property
    def face_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6423.FaceGearSetHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6423,
        )

        return self.__parent__._cast(
            _6423.FaceGearSetHarmonicAnalysisOfSingleExcitation
        )

    @property
    def fe_part_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6424.FEPartHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6424,
        )

        return self.__parent__._cast(_6424.FEPartHarmonicAnalysisOfSingleExcitation)

    @property
    def flexible_pin_assembly_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6425.FlexiblePinAssemblyHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6425,
        )

        return self.__parent__._cast(
            _6425.FlexiblePinAssemblyHarmonicAnalysisOfSingleExcitation
        )

    @property
    def gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6426.GearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6426,
        )

        return self.__parent__._cast(_6426.GearHarmonicAnalysisOfSingleExcitation)

    @property
    def gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6428.GearSetHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6428,
        )

        return self.__parent__._cast(_6428.GearSetHarmonicAnalysisOfSingleExcitation)

    @property
    def guide_dxf_model_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6429.GuideDxfModelHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6429,
        )

        return self.__parent__._cast(
            _6429.GuideDxfModelHarmonicAnalysisOfSingleExcitation
        )

    @property
    def hypoid_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6431.HypoidGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6431,
        )

        return self.__parent__._cast(_6431.HypoidGearHarmonicAnalysisOfSingleExcitation)

    @property
    def hypoid_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6433.HypoidGearSetHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6433,
        )

        return self.__parent__._cast(
            _6433.HypoidGearSetHarmonicAnalysisOfSingleExcitation
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6435.KlingelnbergCycloPalloidConicalGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6435,
        )

        return self.__parent__._cast(
            _6435.KlingelnbergCycloPalloidConicalGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> (
        "_6437.KlingelnbergCycloPalloidConicalGearSetHarmonicAnalysisOfSingleExcitation"
    ):
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6437,
        )

        return self.__parent__._cast(
            _6437.KlingelnbergCycloPalloidConicalGearSetHarmonicAnalysisOfSingleExcitation
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6438.KlingelnbergCycloPalloidHypoidGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6438,
        )

        return self.__parent__._cast(
            _6438.KlingelnbergCycloPalloidHypoidGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> (
        "_6440.KlingelnbergCycloPalloidHypoidGearSetHarmonicAnalysisOfSingleExcitation"
    ):
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6440,
        )

        return self.__parent__._cast(
            _6440.KlingelnbergCycloPalloidHypoidGearSetHarmonicAnalysisOfSingleExcitation
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6441.KlingelnbergCycloPalloidSpiralBevelGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6441,
        )

        return self.__parent__._cast(
            _6441.KlingelnbergCycloPalloidSpiralBevelGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6443.KlingelnbergCycloPalloidSpiralBevelGearSetHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6443,
        )

        return self.__parent__._cast(
            _6443.KlingelnbergCycloPalloidSpiralBevelGearSetHarmonicAnalysisOfSingleExcitation
        )

    @property
    def mass_disc_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6444.MassDiscHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6444,
        )

        return self.__parent__._cast(_6444.MassDiscHarmonicAnalysisOfSingleExcitation)

    @property
    def measurement_component_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6445.MeasurementComponentHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6445,
        )

        return self.__parent__._cast(
            _6445.MeasurementComponentHarmonicAnalysisOfSingleExcitation
        )

    @property
    def microphone_array_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6446.MicrophoneArrayHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6446,
        )

        return self.__parent__._cast(
            _6446.MicrophoneArrayHarmonicAnalysisOfSingleExcitation
        )

    @property
    def microphone_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6447.MicrophoneHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6447,
        )

        return self.__parent__._cast(_6447.MicrophoneHarmonicAnalysisOfSingleExcitation)

    @property
    def mountable_component_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6449.MountableComponentHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6449,
        )

        return self.__parent__._cast(
            _6449.MountableComponentHarmonicAnalysisOfSingleExcitation
        )

    @property
    def oil_seal_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6450.OilSealHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6450,
        )

        return self.__parent__._cast(_6450.OilSealHarmonicAnalysisOfSingleExcitation)

    @property
    def part_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6451.PartHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6451,
        )

        return self.__parent__._cast(_6451.PartHarmonicAnalysisOfSingleExcitation)

    @property
    def part_to_part_shear_coupling_half_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6453.PartToPartShearCouplingHalfHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6453,
        )

        return self.__parent__._cast(
            _6453.PartToPartShearCouplingHalfHarmonicAnalysisOfSingleExcitation
        )

    @property
    def part_to_part_shear_coupling_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6454.PartToPartShearCouplingHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6454,
        )

        return self.__parent__._cast(
            _6454.PartToPartShearCouplingHarmonicAnalysisOfSingleExcitation
        )

    @property
    def planetary_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6456.PlanetaryGearSetHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6456,
        )

        return self.__parent__._cast(
            _6456.PlanetaryGearSetHarmonicAnalysisOfSingleExcitation
        )

    @property
    def planet_carrier_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6457.PlanetCarrierHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6457,
        )

        return self.__parent__._cast(
            _6457.PlanetCarrierHarmonicAnalysisOfSingleExcitation
        )

    @property
    def point_load_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6458.PointLoadHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6458,
        )

        return self.__parent__._cast(_6458.PointLoadHarmonicAnalysisOfSingleExcitation)

    @property
    def power_load_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6459.PowerLoadHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6459,
        )

        return self.__parent__._cast(_6459.PowerLoadHarmonicAnalysisOfSingleExcitation)

    @property
    def pulley_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6460.PulleyHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6460,
        )

        return self.__parent__._cast(_6460.PulleyHarmonicAnalysisOfSingleExcitation)

    @property
    def ring_pins_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6461.RingPinsHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6461,
        )

        return self.__parent__._cast(_6461.RingPinsHarmonicAnalysisOfSingleExcitation)

    @property
    def rolling_ring_assembly_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6463.RollingRingAssemblyHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6463,
        )

        return self.__parent__._cast(
            _6463.RollingRingAssemblyHarmonicAnalysisOfSingleExcitation
        )

    @property
    def rolling_ring_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6465.RollingRingHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6465,
        )

        return self.__parent__._cast(
            _6465.RollingRingHarmonicAnalysisOfSingleExcitation
        )

    @property
    def root_assembly_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6466.RootAssemblyHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6466,
        )

        return self.__parent__._cast(
            _6466.RootAssemblyHarmonicAnalysisOfSingleExcitation
        )

    @property
    def shaft_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6467.ShaftHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6467,
        )

        return self.__parent__._cast(_6467.ShaftHarmonicAnalysisOfSingleExcitation)

    @property
    def shaft_hub_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6468.ShaftHubConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6468,
        )

        return self.__parent__._cast(
            _6468.ShaftHubConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def specialised_assembly_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6470.SpecialisedAssemblyHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6470,
        )

        return self.__parent__._cast(
            _6470.SpecialisedAssemblyHarmonicAnalysisOfSingleExcitation
        )

    @property
    def spiral_bevel_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6471.SpiralBevelGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6471,
        )

        return self.__parent__._cast(
            _6471.SpiralBevelGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def spiral_bevel_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6473.SpiralBevelGearSetHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6473,
        )

        return self.__parent__._cast(
            _6473.SpiralBevelGearSetHarmonicAnalysisOfSingleExcitation
        )

    @property
    def spring_damper_half_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6475.SpringDamperHalfHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6475,
        )

        return self.__parent__._cast(
            _6475.SpringDamperHalfHarmonicAnalysisOfSingleExcitation
        )

    @property
    def spring_damper_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6476.SpringDamperHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6476,
        )

        return self.__parent__._cast(
            _6476.SpringDamperHarmonicAnalysisOfSingleExcitation
        )

    @property
    def straight_bevel_diff_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6477.StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6477,
        )

        return self.__parent__._cast(
            _6477.StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def straight_bevel_diff_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6479.StraightBevelDiffGearSetHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6479,
        )

        return self.__parent__._cast(
            _6479.StraightBevelDiffGearSetHarmonicAnalysisOfSingleExcitation
        )

    @property
    def straight_bevel_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6480.StraightBevelGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6480,
        )

        return self.__parent__._cast(
            _6480.StraightBevelGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def straight_bevel_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6482.StraightBevelGearSetHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6482,
        )

        return self.__parent__._cast(
            _6482.StraightBevelGearSetHarmonicAnalysisOfSingleExcitation
        )

    @property
    def straight_bevel_planet_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6483.StraightBevelPlanetGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6483,
        )

        return self.__parent__._cast(
            _6483.StraightBevelPlanetGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def straight_bevel_sun_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6484.StraightBevelSunGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6484,
        )

        return self.__parent__._cast(
            _6484.StraightBevelSunGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def synchroniser_half_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6485.SynchroniserHalfHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6485,
        )

        return self.__parent__._cast(
            _6485.SynchroniserHalfHarmonicAnalysisOfSingleExcitation
        )

    @property
    def synchroniser_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6486.SynchroniserHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6486,
        )

        return self.__parent__._cast(
            _6486.SynchroniserHarmonicAnalysisOfSingleExcitation
        )

    @property
    def synchroniser_part_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6487.SynchroniserPartHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6487,
        )

        return self.__parent__._cast(
            _6487.SynchroniserPartHarmonicAnalysisOfSingleExcitation
        )

    @property
    def synchroniser_sleeve_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6488.SynchroniserSleeveHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6488,
        )

        return self.__parent__._cast(
            _6488.SynchroniserSleeveHarmonicAnalysisOfSingleExcitation
        )

    @property
    def torque_converter_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6490.TorqueConverterHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6490,
        )

        return self.__parent__._cast(
            _6490.TorqueConverterHarmonicAnalysisOfSingleExcitation
        )

    @property
    def torque_converter_pump_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6491.TorqueConverterPumpHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6491,
        )

        return self.__parent__._cast(
            _6491.TorqueConverterPumpHarmonicAnalysisOfSingleExcitation
        )

    @property
    def torque_converter_turbine_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6492.TorqueConverterTurbineHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6492,
        )

        return self.__parent__._cast(
            _6492.TorqueConverterTurbineHarmonicAnalysisOfSingleExcitation
        )

    @property
    def unbalanced_mass_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6493.UnbalancedMassHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6493,
        )

        return self.__parent__._cast(
            _6493.UnbalancedMassHarmonicAnalysisOfSingleExcitation
        )

    @property
    def virtual_component_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6494.VirtualComponentHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6494,
        )

        return self.__parent__._cast(
            _6494.VirtualComponentHarmonicAnalysisOfSingleExcitation
        )

    @property
    def worm_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6495.WormGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6495,
        )

        return self.__parent__._cast(_6495.WormGearHarmonicAnalysisOfSingleExcitation)

    @property
    def worm_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6497.WormGearSetHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6497,
        )

        return self.__parent__._cast(
            _6497.WormGearSetHarmonicAnalysisOfSingleExcitation
        )

    @property
    def zerol_bevel_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6498.ZerolBevelGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6498,
        )

        return self.__parent__._cast(
            _6498.ZerolBevelGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def zerol_bevel_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6500.ZerolBevelGearSetHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6500,
        )

        return self.__parent__._cast(
            _6500.ZerolBevelGearSetHarmonicAnalysisOfSingleExcitation
        )

    @property
    def abstract_assembly_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6641.AbstractAssemblyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6641,
        )

        return self.__parent__._cast(_6641.AbstractAssemblyDynamicAnalysis)

    @property
    def abstract_shaft_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6642.AbstractShaftDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6642,
        )

        return self.__parent__._cast(_6642.AbstractShaftDynamicAnalysis)

    @property
    def abstract_shaft_or_housing_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6643.AbstractShaftOrHousingDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6643,
        )

        return self.__parent__._cast(_6643.AbstractShaftOrHousingDynamicAnalysis)

    @property
    def agma_gleason_conical_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6645.AGMAGleasonConicalGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6645,
        )

        return self.__parent__._cast(_6645.AGMAGleasonConicalGearDynamicAnalysis)

    @property
    def agma_gleason_conical_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6647.AGMAGleasonConicalGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6647,
        )

        return self.__parent__._cast(_6647.AGMAGleasonConicalGearSetDynamicAnalysis)

    @property
    def assembly_dynamic_analysis(self: "CastSelf") -> "_6648.AssemblyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6648,
        )

        return self.__parent__._cast(_6648.AssemblyDynamicAnalysis)

    @property
    def bearing_dynamic_analysis(self: "CastSelf") -> "_6649.BearingDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6649,
        )

        return self.__parent__._cast(_6649.BearingDynamicAnalysis)

    @property
    def belt_drive_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6651.BeltDriveDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6651,
        )

        return self.__parent__._cast(_6651.BeltDriveDynamicAnalysis)

    @property
    def bevel_differential_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6652.BevelDifferentialGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6652,
        )

        return self.__parent__._cast(_6652.BevelDifferentialGearDynamicAnalysis)

    @property
    def bevel_differential_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6654.BevelDifferentialGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6654,
        )

        return self.__parent__._cast(_6654.BevelDifferentialGearSetDynamicAnalysis)

    @property
    def bevel_differential_planet_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6655.BevelDifferentialPlanetGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6655,
        )

        return self.__parent__._cast(_6655.BevelDifferentialPlanetGearDynamicAnalysis)

    @property
    def bevel_differential_sun_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6656.BevelDifferentialSunGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6656,
        )

        return self.__parent__._cast(_6656.BevelDifferentialSunGearDynamicAnalysis)

    @property
    def bevel_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6657.BevelGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6657,
        )

        return self.__parent__._cast(_6657.BevelGearDynamicAnalysis)

    @property
    def bevel_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6659.BevelGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6659,
        )

        return self.__parent__._cast(_6659.BevelGearSetDynamicAnalysis)

    @property
    def bolt_dynamic_analysis(self: "CastSelf") -> "_6660.BoltDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6660,
        )

        return self.__parent__._cast(_6660.BoltDynamicAnalysis)

    @property
    def bolted_joint_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6661.BoltedJointDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6661,
        )

        return self.__parent__._cast(_6661.BoltedJointDynamicAnalysis)

    @property
    def clutch_dynamic_analysis(self: "CastSelf") -> "_6663.ClutchDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6663,
        )

        return self.__parent__._cast(_6663.ClutchDynamicAnalysis)

    @property
    def clutch_half_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6664.ClutchHalfDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6664,
        )

        return self.__parent__._cast(_6664.ClutchHalfDynamicAnalysis)

    @property
    def component_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6666.ComponentDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6666,
        )

        return self.__parent__._cast(_6666.ComponentDynamicAnalysis)

    @property
    def concept_coupling_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6668.ConceptCouplingDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6668,
        )

        return self.__parent__._cast(_6668.ConceptCouplingDynamicAnalysis)

    @property
    def concept_coupling_half_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6669.ConceptCouplingHalfDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6669,
        )

        return self.__parent__._cast(_6669.ConceptCouplingHalfDynamicAnalysis)

    @property
    def concept_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6670.ConceptGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6670,
        )

        return self.__parent__._cast(_6670.ConceptGearDynamicAnalysis)

    @property
    def concept_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6672.ConceptGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6672,
        )

        return self.__parent__._cast(_6672.ConceptGearSetDynamicAnalysis)

    @property
    def conical_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6673.ConicalGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6673,
        )

        return self.__parent__._cast(_6673.ConicalGearDynamicAnalysis)

    @property
    def conical_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6675.ConicalGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6675,
        )

        return self.__parent__._cast(_6675.ConicalGearSetDynamicAnalysis)

    @property
    def connector_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6677.ConnectorDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6677,
        )

        return self.__parent__._cast(_6677.ConnectorDynamicAnalysis)

    @property
    def coupling_dynamic_analysis(self: "CastSelf") -> "_6679.CouplingDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6679,
        )

        return self.__parent__._cast(_6679.CouplingDynamicAnalysis)

    @property
    def coupling_half_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6680.CouplingHalfDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6680,
        )

        return self.__parent__._cast(_6680.CouplingHalfDynamicAnalysis)

    @property
    def cvt_dynamic_analysis(self: "CastSelf") -> "_6682.CVTDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6682,
        )

        return self.__parent__._cast(_6682.CVTDynamicAnalysis)

    @property
    def cvt_pulley_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6683.CVTPulleyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6683,
        )

        return self.__parent__._cast(_6683.CVTPulleyDynamicAnalysis)

    @property
    def cycloidal_assembly_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6684.CycloidalAssemblyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6684,
        )

        return self.__parent__._cast(_6684.CycloidalAssemblyDynamicAnalysis)

    @property
    def cycloidal_disc_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6686.CycloidalDiscDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6686,
        )

        return self.__parent__._cast(_6686.CycloidalDiscDynamicAnalysis)

    @property
    def cylindrical_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6688.CylindricalGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6688,
        )

        return self.__parent__._cast(_6688.CylindricalGearDynamicAnalysis)

    @property
    def cylindrical_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6690.CylindricalGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6690,
        )

        return self.__parent__._cast(_6690.CylindricalGearSetDynamicAnalysis)

    @property
    def cylindrical_planet_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6691.CylindricalPlanetGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6691,
        )

        return self.__parent__._cast(_6691.CylindricalPlanetGearDynamicAnalysis)

    @property
    def datum_dynamic_analysis(self: "CastSelf") -> "_6692.DatumDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6692,
        )

        return self.__parent__._cast(_6692.DatumDynamicAnalysis)

    @property
    def external_cad_model_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6695.ExternalCADModelDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6695,
        )

        return self.__parent__._cast(_6695.ExternalCADModelDynamicAnalysis)

    @property
    def face_gear_dynamic_analysis(self: "CastSelf") -> "_6696.FaceGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6696,
        )

        return self.__parent__._cast(_6696.FaceGearDynamicAnalysis)

    @property
    def face_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6698.FaceGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6698,
        )

        return self.__parent__._cast(_6698.FaceGearSetDynamicAnalysis)

    @property
    def fe_part_dynamic_analysis(self: "CastSelf") -> "_6699.FEPartDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6699,
        )

        return self.__parent__._cast(_6699.FEPartDynamicAnalysis)

    @property
    def flexible_pin_assembly_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6700.FlexiblePinAssemblyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6700,
        )

        return self.__parent__._cast(_6700.FlexiblePinAssemblyDynamicAnalysis)

    @property
    def gear_dynamic_analysis(self: "CastSelf") -> "_6701.GearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6701,
        )

        return self.__parent__._cast(_6701.GearDynamicAnalysis)

    @property
    def gear_set_dynamic_analysis(self: "CastSelf") -> "_6703.GearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6703,
        )

        return self.__parent__._cast(_6703.GearSetDynamicAnalysis)

    @property
    def guide_dxf_model_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6704.GuideDxfModelDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6704,
        )

        return self.__parent__._cast(_6704.GuideDxfModelDynamicAnalysis)

    @property
    def hypoid_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6705.HypoidGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6705,
        )

        return self.__parent__._cast(_6705.HypoidGearDynamicAnalysis)

    @property
    def hypoid_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6707.HypoidGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6707,
        )

        return self.__parent__._cast(_6707.HypoidGearSetDynamicAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6709.KlingelnbergCycloPalloidConicalGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6709,
        )

        return self.__parent__._cast(
            _6709.KlingelnbergCycloPalloidConicalGearDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6711.KlingelnbergCycloPalloidConicalGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6711,
        )

        return self.__parent__._cast(
            _6711.KlingelnbergCycloPalloidConicalGearSetDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6712.KlingelnbergCycloPalloidHypoidGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6712,
        )

        return self.__parent__._cast(
            _6712.KlingelnbergCycloPalloidHypoidGearDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6714.KlingelnbergCycloPalloidHypoidGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6714,
        )

        return self.__parent__._cast(
            _6714.KlingelnbergCycloPalloidHypoidGearSetDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6715.KlingelnbergCycloPalloidSpiralBevelGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6715,
        )

        return self.__parent__._cast(
            _6715.KlingelnbergCycloPalloidSpiralBevelGearDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6717.KlingelnbergCycloPalloidSpiralBevelGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6717,
        )

        return self.__parent__._cast(
            _6717.KlingelnbergCycloPalloidSpiralBevelGearSetDynamicAnalysis
        )

    @property
    def mass_disc_dynamic_analysis(self: "CastSelf") -> "_6718.MassDiscDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6718,
        )

        return self.__parent__._cast(_6718.MassDiscDynamicAnalysis)

    @property
    def measurement_component_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6719.MeasurementComponentDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6719,
        )

        return self.__parent__._cast(_6719.MeasurementComponentDynamicAnalysis)

    @property
    def microphone_array_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6720.MicrophoneArrayDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6720,
        )

        return self.__parent__._cast(_6720.MicrophoneArrayDynamicAnalysis)

    @property
    def microphone_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6721.MicrophoneDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6721,
        )

        return self.__parent__._cast(_6721.MicrophoneDynamicAnalysis)

    @property
    def mountable_component_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6722.MountableComponentDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6722,
        )

        return self.__parent__._cast(_6722.MountableComponentDynamicAnalysis)

    @property
    def oil_seal_dynamic_analysis(self: "CastSelf") -> "_6723.OilSealDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6723,
        )

        return self.__parent__._cast(_6723.OilSealDynamicAnalysis)

    @property
    def part_dynamic_analysis(self: "CastSelf") -> "_6724.PartDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6724,
        )

        return self.__parent__._cast(_6724.PartDynamicAnalysis)

    @property
    def part_to_part_shear_coupling_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6726.PartToPartShearCouplingDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6726,
        )

        return self.__parent__._cast(_6726.PartToPartShearCouplingDynamicAnalysis)

    @property
    def part_to_part_shear_coupling_half_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6727.PartToPartShearCouplingHalfDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6727,
        )

        return self.__parent__._cast(_6727.PartToPartShearCouplingHalfDynamicAnalysis)

    @property
    def planetary_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6729.PlanetaryGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6729,
        )

        return self.__parent__._cast(_6729.PlanetaryGearSetDynamicAnalysis)

    @property
    def planet_carrier_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6730.PlanetCarrierDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6730,
        )

        return self.__parent__._cast(_6730.PlanetCarrierDynamicAnalysis)

    @property
    def point_load_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6731.PointLoadDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6731,
        )

        return self.__parent__._cast(_6731.PointLoadDynamicAnalysis)

    @property
    def power_load_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6732.PowerLoadDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6732,
        )

        return self.__parent__._cast(_6732.PowerLoadDynamicAnalysis)

    @property
    def pulley_dynamic_analysis(self: "CastSelf") -> "_6733.PulleyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6733,
        )

        return self.__parent__._cast(_6733.PulleyDynamicAnalysis)

    @property
    def ring_pins_dynamic_analysis(self: "CastSelf") -> "_6734.RingPinsDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6734,
        )

        return self.__parent__._cast(_6734.RingPinsDynamicAnalysis)

    @property
    def rolling_ring_assembly_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6736.RollingRingAssemblyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6736,
        )

        return self.__parent__._cast(_6736.RollingRingAssemblyDynamicAnalysis)

    @property
    def rolling_ring_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6738.RollingRingDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6738,
        )

        return self.__parent__._cast(_6738.RollingRingDynamicAnalysis)

    @property
    def root_assembly_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6739.RootAssemblyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6739,
        )

        return self.__parent__._cast(_6739.RootAssemblyDynamicAnalysis)

    @property
    def shaft_dynamic_analysis(self: "CastSelf") -> "_6740.ShaftDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6740,
        )

        return self.__parent__._cast(_6740.ShaftDynamicAnalysis)

    @property
    def shaft_hub_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6741.ShaftHubConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6741,
        )

        return self.__parent__._cast(_6741.ShaftHubConnectionDynamicAnalysis)

    @property
    def specialised_assembly_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6743.SpecialisedAssemblyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6743,
        )

        return self.__parent__._cast(_6743.SpecialisedAssemblyDynamicAnalysis)

    @property
    def spiral_bevel_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6744.SpiralBevelGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6744,
        )

        return self.__parent__._cast(_6744.SpiralBevelGearDynamicAnalysis)

    @property
    def spiral_bevel_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6746.SpiralBevelGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6746,
        )

        return self.__parent__._cast(_6746.SpiralBevelGearSetDynamicAnalysis)

    @property
    def spring_damper_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6748.SpringDamperDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6748,
        )

        return self.__parent__._cast(_6748.SpringDamperDynamicAnalysis)

    @property
    def spring_damper_half_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6749.SpringDamperHalfDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6749,
        )

        return self.__parent__._cast(_6749.SpringDamperHalfDynamicAnalysis)

    @property
    def straight_bevel_diff_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6750.StraightBevelDiffGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6750,
        )

        return self.__parent__._cast(_6750.StraightBevelDiffGearDynamicAnalysis)

    @property
    def straight_bevel_diff_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6752.StraightBevelDiffGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6752,
        )

        return self.__parent__._cast(_6752.StraightBevelDiffGearSetDynamicAnalysis)

    @property
    def straight_bevel_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6753.StraightBevelGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6753,
        )

        return self.__parent__._cast(_6753.StraightBevelGearDynamicAnalysis)

    @property
    def straight_bevel_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6755.StraightBevelGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6755,
        )

        return self.__parent__._cast(_6755.StraightBevelGearSetDynamicAnalysis)

    @property
    def straight_bevel_planet_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6756.StraightBevelPlanetGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6756,
        )

        return self.__parent__._cast(_6756.StraightBevelPlanetGearDynamicAnalysis)

    @property
    def straight_bevel_sun_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6757.StraightBevelSunGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6757,
        )

        return self.__parent__._cast(_6757.StraightBevelSunGearDynamicAnalysis)

    @property
    def synchroniser_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6758.SynchroniserDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6758,
        )

        return self.__parent__._cast(_6758.SynchroniserDynamicAnalysis)

    @property
    def synchroniser_half_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6759.SynchroniserHalfDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6759,
        )

        return self.__parent__._cast(_6759.SynchroniserHalfDynamicAnalysis)

    @property
    def synchroniser_part_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6760.SynchroniserPartDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6760,
        )

        return self.__parent__._cast(_6760.SynchroniserPartDynamicAnalysis)

    @property
    def synchroniser_sleeve_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6761.SynchroniserSleeveDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6761,
        )

        return self.__parent__._cast(_6761.SynchroniserSleeveDynamicAnalysis)

    @property
    def torque_converter_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6763.TorqueConverterDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6763,
        )

        return self.__parent__._cast(_6763.TorqueConverterDynamicAnalysis)

    @property
    def torque_converter_pump_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6764.TorqueConverterPumpDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6764,
        )

        return self.__parent__._cast(_6764.TorqueConverterPumpDynamicAnalysis)

    @property
    def torque_converter_turbine_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6765.TorqueConverterTurbineDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6765,
        )

        return self.__parent__._cast(_6765.TorqueConverterTurbineDynamicAnalysis)

    @property
    def unbalanced_mass_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6766.UnbalancedMassDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6766,
        )

        return self.__parent__._cast(_6766.UnbalancedMassDynamicAnalysis)

    @property
    def virtual_component_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6767.VirtualComponentDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6767,
        )

        return self.__parent__._cast(_6767.VirtualComponentDynamicAnalysis)

    @property
    def worm_gear_dynamic_analysis(self: "CastSelf") -> "_6768.WormGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6768,
        )

        return self.__parent__._cast(_6768.WormGearDynamicAnalysis)

    @property
    def worm_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6770.WormGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6770,
        )

        return self.__parent__._cast(_6770.WormGearSetDynamicAnalysis)

    @property
    def zerol_bevel_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6771.ZerolBevelGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6771,
        )

        return self.__parent__._cast(_6771.ZerolBevelGearDynamicAnalysis)

    @property
    def zerol_bevel_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6773.ZerolBevelGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6773,
        )

        return self.__parent__._cast(_6773.ZerolBevelGearSetDynamicAnalysis)

    @property
    def abstract_assembly_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6911.AbstractAssemblyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6911,
        )

        return self.__parent__._cast(_6911.AbstractAssemblyCriticalSpeedAnalysis)

    @property
    def abstract_shaft_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6912.AbstractShaftCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6912,
        )

        return self.__parent__._cast(_6912.AbstractShaftCriticalSpeedAnalysis)

    @property
    def abstract_shaft_or_housing_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6913.AbstractShaftOrHousingCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6913,
        )

        return self.__parent__._cast(_6913.AbstractShaftOrHousingCriticalSpeedAnalysis)

    @property
    def agma_gleason_conical_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6915.AGMAGleasonConicalGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6915,
        )

        return self.__parent__._cast(_6915.AGMAGleasonConicalGearCriticalSpeedAnalysis)

    @property
    def agma_gleason_conical_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6917.AGMAGleasonConicalGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6917,
        )

        return self.__parent__._cast(
            _6917.AGMAGleasonConicalGearSetCriticalSpeedAnalysis
        )

    @property
    def assembly_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6918.AssemblyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6918,
        )

        return self.__parent__._cast(_6918.AssemblyCriticalSpeedAnalysis)

    @property
    def bearing_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6919.BearingCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6919,
        )

        return self.__parent__._cast(_6919.BearingCriticalSpeedAnalysis)

    @property
    def belt_drive_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6921.BeltDriveCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6921,
        )

        return self.__parent__._cast(_6921.BeltDriveCriticalSpeedAnalysis)

    @property
    def bevel_differential_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6922.BevelDifferentialGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6922,
        )

        return self.__parent__._cast(_6922.BevelDifferentialGearCriticalSpeedAnalysis)

    @property
    def bevel_differential_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6924.BevelDifferentialGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6924,
        )

        return self.__parent__._cast(
            _6924.BevelDifferentialGearSetCriticalSpeedAnalysis
        )

    @property
    def bevel_differential_planet_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6925.BevelDifferentialPlanetGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6925,
        )

        return self.__parent__._cast(
            _6925.BevelDifferentialPlanetGearCriticalSpeedAnalysis
        )

    @property
    def bevel_differential_sun_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6926.BevelDifferentialSunGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6926,
        )

        return self.__parent__._cast(
            _6926.BevelDifferentialSunGearCriticalSpeedAnalysis
        )

    @property
    def bevel_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6927.BevelGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6927,
        )

        return self.__parent__._cast(_6927.BevelGearCriticalSpeedAnalysis)

    @property
    def bevel_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6929.BevelGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6929,
        )

        return self.__parent__._cast(_6929.BevelGearSetCriticalSpeedAnalysis)

    @property
    def bolt_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6930.BoltCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6930,
        )

        return self.__parent__._cast(_6930.BoltCriticalSpeedAnalysis)

    @property
    def bolted_joint_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6931.BoltedJointCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6931,
        )

        return self.__parent__._cast(_6931.BoltedJointCriticalSpeedAnalysis)

    @property
    def clutch_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6933.ClutchCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6933,
        )

        return self.__parent__._cast(_6933.ClutchCriticalSpeedAnalysis)

    @property
    def clutch_half_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6934.ClutchHalfCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6934,
        )

        return self.__parent__._cast(_6934.ClutchHalfCriticalSpeedAnalysis)

    @property
    def component_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6936.ComponentCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6936,
        )

        return self.__parent__._cast(_6936.ComponentCriticalSpeedAnalysis)

    @property
    def concept_coupling_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6938.ConceptCouplingCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6938,
        )

        return self.__parent__._cast(_6938.ConceptCouplingCriticalSpeedAnalysis)

    @property
    def concept_coupling_half_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6939.ConceptCouplingHalfCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6939,
        )

        return self.__parent__._cast(_6939.ConceptCouplingHalfCriticalSpeedAnalysis)

    @property
    def concept_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6940.ConceptGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6940,
        )

        return self.__parent__._cast(_6940.ConceptGearCriticalSpeedAnalysis)

    @property
    def concept_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6942.ConceptGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6942,
        )

        return self.__parent__._cast(_6942.ConceptGearSetCriticalSpeedAnalysis)

    @property
    def conical_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6943.ConicalGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6943,
        )

        return self.__parent__._cast(_6943.ConicalGearCriticalSpeedAnalysis)

    @property
    def conical_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6945.ConicalGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6945,
        )

        return self.__parent__._cast(_6945.ConicalGearSetCriticalSpeedAnalysis)

    @property
    def connector_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6947.ConnectorCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6947,
        )

        return self.__parent__._cast(_6947.ConnectorCriticalSpeedAnalysis)

    @property
    def coupling_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6949.CouplingCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6949,
        )

        return self.__parent__._cast(_6949.CouplingCriticalSpeedAnalysis)

    @property
    def coupling_half_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6950.CouplingHalfCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6950,
        )

        return self.__parent__._cast(_6950.CouplingHalfCriticalSpeedAnalysis)

    @property
    def cvt_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6955.CVTCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6955,
        )

        return self.__parent__._cast(_6955.CVTCriticalSpeedAnalysis)

    @property
    def cvt_pulley_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6956.CVTPulleyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6956,
        )

        return self.__parent__._cast(_6956.CVTPulleyCriticalSpeedAnalysis)

    @property
    def cycloidal_assembly_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6957.CycloidalAssemblyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6957,
        )

        return self.__parent__._cast(_6957.CycloidalAssemblyCriticalSpeedAnalysis)

    @property
    def cycloidal_disc_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6959.CycloidalDiscCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6959,
        )

        return self.__parent__._cast(_6959.CycloidalDiscCriticalSpeedAnalysis)

    @property
    def cylindrical_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6961.CylindricalGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6961,
        )

        return self.__parent__._cast(_6961.CylindricalGearCriticalSpeedAnalysis)

    @property
    def cylindrical_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6963.CylindricalGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6963,
        )

        return self.__parent__._cast(_6963.CylindricalGearSetCriticalSpeedAnalysis)

    @property
    def cylindrical_planet_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6964.CylindricalPlanetGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6964,
        )

        return self.__parent__._cast(_6964.CylindricalPlanetGearCriticalSpeedAnalysis)

    @property
    def datum_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6965.DatumCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6965,
        )

        return self.__parent__._cast(_6965.DatumCriticalSpeedAnalysis)

    @property
    def external_cad_model_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6966.ExternalCADModelCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6966,
        )

        return self.__parent__._cast(_6966.ExternalCADModelCriticalSpeedAnalysis)

    @property
    def face_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6967.FaceGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6967,
        )

        return self.__parent__._cast(_6967.FaceGearCriticalSpeedAnalysis)

    @property
    def face_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6969.FaceGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6969,
        )

        return self.__parent__._cast(_6969.FaceGearSetCriticalSpeedAnalysis)

    @property
    def fe_part_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6970.FEPartCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6970,
        )

        return self.__parent__._cast(_6970.FEPartCriticalSpeedAnalysis)

    @property
    def flexible_pin_assembly_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6971.FlexiblePinAssemblyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6971,
        )

        return self.__parent__._cast(_6971.FlexiblePinAssemblyCriticalSpeedAnalysis)

    @property
    def gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6972.GearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6972,
        )

        return self.__parent__._cast(_6972.GearCriticalSpeedAnalysis)

    @property
    def gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6974.GearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6974,
        )

        return self.__parent__._cast(_6974.GearSetCriticalSpeedAnalysis)

    @property
    def guide_dxf_model_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6975.GuideDxfModelCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6975,
        )

        return self.__parent__._cast(_6975.GuideDxfModelCriticalSpeedAnalysis)

    @property
    def hypoid_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6976.HypoidGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6976,
        )

        return self.__parent__._cast(_6976.HypoidGearCriticalSpeedAnalysis)

    @property
    def hypoid_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6978.HypoidGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6978,
        )

        return self.__parent__._cast(_6978.HypoidGearSetCriticalSpeedAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6980.KlingelnbergCycloPalloidConicalGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6980,
        )

        return self.__parent__._cast(
            _6980.KlingelnbergCycloPalloidConicalGearCriticalSpeedAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6982.KlingelnbergCycloPalloidConicalGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6982,
        )

        return self.__parent__._cast(
            _6982.KlingelnbergCycloPalloidConicalGearSetCriticalSpeedAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6983.KlingelnbergCycloPalloidHypoidGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6983,
        )

        return self.__parent__._cast(
            _6983.KlingelnbergCycloPalloidHypoidGearCriticalSpeedAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6985.KlingelnbergCycloPalloidHypoidGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6985,
        )

        return self.__parent__._cast(
            _6985.KlingelnbergCycloPalloidHypoidGearSetCriticalSpeedAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6986.KlingelnbergCycloPalloidSpiralBevelGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6986,
        )

        return self.__parent__._cast(
            _6986.KlingelnbergCycloPalloidSpiralBevelGearCriticalSpeedAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6988.KlingelnbergCycloPalloidSpiralBevelGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6988,
        )

        return self.__parent__._cast(
            _6988.KlingelnbergCycloPalloidSpiralBevelGearSetCriticalSpeedAnalysis
        )

    @property
    def mass_disc_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6989.MassDiscCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6989,
        )

        return self.__parent__._cast(_6989.MassDiscCriticalSpeedAnalysis)

    @property
    def measurement_component_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6990.MeasurementComponentCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6990,
        )

        return self.__parent__._cast(_6990.MeasurementComponentCriticalSpeedAnalysis)

    @property
    def microphone_array_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6991.MicrophoneArrayCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6991,
        )

        return self.__parent__._cast(_6991.MicrophoneArrayCriticalSpeedAnalysis)

    @property
    def microphone_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6992.MicrophoneCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6992,
        )

        return self.__parent__._cast(_6992.MicrophoneCriticalSpeedAnalysis)

    @property
    def mountable_component_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6993.MountableComponentCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6993,
        )

        return self.__parent__._cast(_6993.MountableComponentCriticalSpeedAnalysis)

    @property
    def oil_seal_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6994.OilSealCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6994,
        )

        return self.__parent__._cast(_6994.OilSealCriticalSpeedAnalysis)

    @property
    def part_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6995.PartCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6995,
        )

        return self.__parent__._cast(_6995.PartCriticalSpeedAnalysis)

    @property
    def part_to_part_shear_coupling_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6997.PartToPartShearCouplingCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6997,
        )

        return self.__parent__._cast(_6997.PartToPartShearCouplingCriticalSpeedAnalysis)

    @property
    def part_to_part_shear_coupling_half_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6998.PartToPartShearCouplingHalfCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6998,
        )

        return self.__parent__._cast(
            _6998.PartToPartShearCouplingHalfCriticalSpeedAnalysis
        )

    @property
    def planetary_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7000.PlanetaryGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7000,
        )

        return self.__parent__._cast(_7000.PlanetaryGearSetCriticalSpeedAnalysis)

    @property
    def planet_carrier_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7001.PlanetCarrierCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7001,
        )

        return self.__parent__._cast(_7001.PlanetCarrierCriticalSpeedAnalysis)

    @property
    def point_load_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7002.PointLoadCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7002,
        )

        return self.__parent__._cast(_7002.PointLoadCriticalSpeedAnalysis)

    @property
    def power_load_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7003.PowerLoadCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7003,
        )

        return self.__parent__._cast(_7003.PowerLoadCriticalSpeedAnalysis)

    @property
    def pulley_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7004.PulleyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7004,
        )

        return self.__parent__._cast(_7004.PulleyCriticalSpeedAnalysis)

    @property
    def ring_pins_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7005.RingPinsCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7005,
        )

        return self.__parent__._cast(_7005.RingPinsCriticalSpeedAnalysis)

    @property
    def rolling_ring_assembly_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7007.RollingRingAssemblyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7007,
        )

        return self.__parent__._cast(_7007.RollingRingAssemblyCriticalSpeedAnalysis)

    @property
    def rolling_ring_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7009.RollingRingCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7009,
        )

        return self.__parent__._cast(_7009.RollingRingCriticalSpeedAnalysis)

    @property
    def root_assembly_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7010.RootAssemblyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7010,
        )

        return self.__parent__._cast(_7010.RootAssemblyCriticalSpeedAnalysis)

    @property
    def shaft_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7011.ShaftCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7011,
        )

        return self.__parent__._cast(_7011.ShaftCriticalSpeedAnalysis)

    @property
    def shaft_hub_connection_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7012.ShaftHubConnectionCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7012,
        )

        return self.__parent__._cast(_7012.ShaftHubConnectionCriticalSpeedAnalysis)

    @property
    def specialised_assembly_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7014.SpecialisedAssemblyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7014,
        )

        return self.__parent__._cast(_7014.SpecialisedAssemblyCriticalSpeedAnalysis)

    @property
    def spiral_bevel_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7015.SpiralBevelGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7015,
        )

        return self.__parent__._cast(_7015.SpiralBevelGearCriticalSpeedAnalysis)

    @property
    def spiral_bevel_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7017.SpiralBevelGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7017,
        )

        return self.__parent__._cast(_7017.SpiralBevelGearSetCriticalSpeedAnalysis)

    @property
    def spring_damper_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7019.SpringDamperCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7019,
        )

        return self.__parent__._cast(_7019.SpringDamperCriticalSpeedAnalysis)

    @property
    def spring_damper_half_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7020.SpringDamperHalfCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7020,
        )

        return self.__parent__._cast(_7020.SpringDamperHalfCriticalSpeedAnalysis)

    @property
    def straight_bevel_diff_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7021.StraightBevelDiffGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7021,
        )

        return self.__parent__._cast(_7021.StraightBevelDiffGearCriticalSpeedAnalysis)

    @property
    def straight_bevel_diff_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7023.StraightBevelDiffGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7023,
        )

        return self.__parent__._cast(
            _7023.StraightBevelDiffGearSetCriticalSpeedAnalysis
        )

    @property
    def straight_bevel_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7024.StraightBevelGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7024,
        )

        return self.__parent__._cast(_7024.StraightBevelGearCriticalSpeedAnalysis)

    @property
    def straight_bevel_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7026.StraightBevelGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7026,
        )

        return self.__parent__._cast(_7026.StraightBevelGearSetCriticalSpeedAnalysis)

    @property
    def straight_bevel_planet_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7027.StraightBevelPlanetGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7027,
        )

        return self.__parent__._cast(_7027.StraightBevelPlanetGearCriticalSpeedAnalysis)

    @property
    def straight_bevel_sun_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7028.StraightBevelSunGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7028,
        )

        return self.__parent__._cast(_7028.StraightBevelSunGearCriticalSpeedAnalysis)

    @property
    def synchroniser_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7029.SynchroniserCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7029,
        )

        return self.__parent__._cast(_7029.SynchroniserCriticalSpeedAnalysis)

    @property
    def synchroniser_half_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7030.SynchroniserHalfCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7030,
        )

        return self.__parent__._cast(_7030.SynchroniserHalfCriticalSpeedAnalysis)

    @property
    def synchroniser_part_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7031.SynchroniserPartCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7031,
        )

        return self.__parent__._cast(_7031.SynchroniserPartCriticalSpeedAnalysis)

    @property
    def synchroniser_sleeve_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7032.SynchroniserSleeveCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7032,
        )

        return self.__parent__._cast(_7032.SynchroniserSleeveCriticalSpeedAnalysis)

    @property
    def torque_converter_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7034.TorqueConverterCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7034,
        )

        return self.__parent__._cast(_7034.TorqueConverterCriticalSpeedAnalysis)

    @property
    def torque_converter_pump_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7035.TorqueConverterPumpCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7035,
        )

        return self.__parent__._cast(_7035.TorqueConverterPumpCriticalSpeedAnalysis)

    @property
    def torque_converter_turbine_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7036.TorqueConverterTurbineCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7036,
        )

        return self.__parent__._cast(_7036.TorqueConverterTurbineCriticalSpeedAnalysis)

    @property
    def unbalanced_mass_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7037.UnbalancedMassCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7037,
        )

        return self.__parent__._cast(_7037.UnbalancedMassCriticalSpeedAnalysis)

    @property
    def virtual_component_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7038.VirtualComponentCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7038,
        )

        return self.__parent__._cast(_7038.VirtualComponentCriticalSpeedAnalysis)

    @property
    def worm_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7039.WormGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7039,
        )

        return self.__parent__._cast(_7039.WormGearCriticalSpeedAnalysis)

    @property
    def worm_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7041.WormGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7041,
        )

        return self.__parent__._cast(_7041.WormGearSetCriticalSpeedAnalysis)

    @property
    def zerol_bevel_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7042.ZerolBevelGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7042,
        )

        return self.__parent__._cast(_7042.ZerolBevelGearCriticalSpeedAnalysis)

    @property
    def zerol_bevel_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7044.ZerolBevelGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7044,
        )

        return self.__parent__._cast(_7044.ZerolBevelGearSetCriticalSpeedAnalysis)

    @property
    def abstract_assembly_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7176.AbstractAssemblyAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7176,
        )

        return self.__parent__._cast(
            _7176.AbstractAssemblyAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def abstract_shaft_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7177.AbstractShaftAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7177,
        )

        return self.__parent__._cast(
            _7177.AbstractShaftAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def abstract_shaft_or_housing_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7178.AbstractShaftOrHousingAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7178,
        )

        return self.__parent__._cast(
            _7178.AbstractShaftOrHousingAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def agma_gleason_conical_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7184.AGMAGleasonConicalGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7184,
        )

        return self.__parent__._cast(
            _7184.AGMAGleasonConicalGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def agma_gleason_conical_gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7186.AGMAGleasonConicalGearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7186,
        )

        return self.__parent__._cast(
            _7186.AGMAGleasonConicalGearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def assembly_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7187.AssemblyAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7187,
        )

        return self.__parent__._cast(
            _7187.AssemblyAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def bearing_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7189.BearingAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7189,
        )

        return self.__parent__._cast(
            _7189.BearingAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def belt_drive_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7191.BeltDriveAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7191,
        )

        return self.__parent__._cast(
            _7191.BeltDriveAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def bevel_differential_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7192.BevelDifferentialGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7192,
        )

        return self.__parent__._cast(
            _7192.BevelDifferentialGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def bevel_differential_gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7194.BevelDifferentialGearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7194,
        )

        return self.__parent__._cast(
            _7194.BevelDifferentialGearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def bevel_differential_planet_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7195.BevelDifferentialPlanetGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7195,
        )

        return self.__parent__._cast(
            _7195.BevelDifferentialPlanetGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def bevel_differential_sun_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7196.BevelDifferentialSunGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7196,
        )

        return self.__parent__._cast(
            _7196.BevelDifferentialSunGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def bevel_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7197.BevelGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7197,
        )

        return self.__parent__._cast(
            _7197.BevelGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def bevel_gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7199.BevelGearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7199,
        )

        return self.__parent__._cast(
            _7199.BevelGearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def bolt_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7200.BoltAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7200,
        )

        return self.__parent__._cast(
            _7200.BoltAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def bolted_joint_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7201.BoltedJointAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7201,
        )

        return self.__parent__._cast(
            _7201.BoltedJointAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def clutch_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7202.ClutchAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7202,
        )

        return self.__parent__._cast(
            _7202.ClutchAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def clutch_half_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7204.ClutchHalfAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7204,
        )

        return self.__parent__._cast(
            _7204.ClutchHalfAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def component_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7206.ComponentAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7206,
        )

        return self.__parent__._cast(
            _7206.ComponentAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def concept_coupling_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7207.ConceptCouplingAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7207,
        )

        return self.__parent__._cast(
            _7207.ConceptCouplingAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def concept_coupling_half_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7209.ConceptCouplingHalfAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7209,
        )

        return self.__parent__._cast(
            _7209.ConceptCouplingHalfAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def concept_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7210.ConceptGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7210,
        )

        return self.__parent__._cast(
            _7210.ConceptGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def concept_gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7212.ConceptGearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7212,
        )

        return self.__parent__._cast(
            _7212.ConceptGearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def conical_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7213.ConicalGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7213,
        )

        return self.__parent__._cast(
            _7213.ConicalGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def conical_gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7215.ConicalGearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7215,
        )

        return self.__parent__._cast(
            _7215.ConicalGearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def connector_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7217.ConnectorAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7217,
        )

        return self.__parent__._cast(
            _7217.ConnectorAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def coupling_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7218.CouplingAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7218,
        )

        return self.__parent__._cast(
            _7218.CouplingAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def coupling_half_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7220.CouplingHalfAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7220,
        )

        return self.__parent__._cast(
            _7220.CouplingHalfAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def cvt_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7221.CVTAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7221,
        )

        return self.__parent__._cast(_7221.CVTAdvancedTimeSteppingAnalysisForModulation)

    @property
    def cvt_pulley_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7223.CVTPulleyAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7223,
        )

        return self.__parent__._cast(
            _7223.CVTPulleyAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def cycloidal_assembly_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7224.CycloidalAssemblyAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7224,
        )

        return self.__parent__._cast(
            _7224.CycloidalAssemblyAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def cycloidal_disc_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7225.CycloidalDiscAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7225,
        )

        return self.__parent__._cast(
            _7225.CycloidalDiscAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def cylindrical_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7228.CylindricalGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7228,
        )

        return self.__parent__._cast(
            _7228.CylindricalGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def cylindrical_gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7230.CylindricalGearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7230,
        )

        return self.__parent__._cast(
            _7230.CylindricalGearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def cylindrical_planet_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7231.CylindricalPlanetGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7231,
        )

        return self.__parent__._cast(
            _7231.CylindricalPlanetGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def datum_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7232.DatumAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7232,
        )

        return self.__parent__._cast(
            _7232.DatumAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def external_cad_model_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7233.ExternalCADModelAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7233,
        )

        return self.__parent__._cast(
            _7233.ExternalCADModelAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def face_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7234.FaceGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7234,
        )

        return self.__parent__._cast(
            _7234.FaceGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def face_gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7236.FaceGearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7236,
        )

        return self.__parent__._cast(
            _7236.FaceGearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def fe_part_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7237.FEPartAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7237,
        )

        return self.__parent__._cast(
            _7237.FEPartAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def flexible_pin_assembly_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7238.FlexiblePinAssemblyAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7238,
        )

        return self.__parent__._cast(
            _7238.FlexiblePinAssemblyAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7239.GearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7239,
        )

        return self.__parent__._cast(
            _7239.GearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7241.GearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7241,
        )

        return self.__parent__._cast(
            _7241.GearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def guide_dxf_model_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7242.GuideDxfModelAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7242,
        )

        return self.__parent__._cast(
            _7242.GuideDxfModelAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def hypoid_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7244.HypoidGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7244,
        )

        return self.__parent__._cast(
            _7244.HypoidGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def hypoid_gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7246.HypoidGearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7246,
        )

        return self.__parent__._cast(
            _7246.HypoidGearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7248.KlingelnbergCycloPalloidConicalGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7248,
        )

        return self.__parent__._cast(
            _7248.KlingelnbergCycloPalloidConicalGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7250.KlingelnbergCycloPalloidConicalGearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7250,
        )

        return self.__parent__._cast(
            _7250.KlingelnbergCycloPalloidConicalGearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7251.KlingelnbergCycloPalloidHypoidGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7251,
        )

        return self.__parent__._cast(
            _7251.KlingelnbergCycloPalloidHypoidGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7253.KlingelnbergCycloPalloidHypoidGearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7253,
        )

        return self.__parent__._cast(
            _7253.KlingelnbergCycloPalloidHypoidGearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7254.KlingelnbergCycloPalloidSpiralBevelGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7254,
        )

        return self.__parent__._cast(
            _7254.KlingelnbergCycloPalloidSpiralBevelGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7256.KlingelnbergCycloPalloidSpiralBevelGearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7256,
        )

        return self.__parent__._cast(
            _7256.KlingelnbergCycloPalloidSpiralBevelGearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def mass_disc_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7257.MassDiscAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7257,
        )

        return self.__parent__._cast(
            _7257.MassDiscAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def measurement_component_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7258.MeasurementComponentAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7258,
        )

        return self.__parent__._cast(
            _7258.MeasurementComponentAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def microphone_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7259.MicrophoneAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7259,
        )

        return self.__parent__._cast(
            _7259.MicrophoneAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def microphone_array_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7260.MicrophoneArrayAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7260,
        )

        return self.__parent__._cast(
            _7260.MicrophoneArrayAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def mountable_component_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7261.MountableComponentAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7261,
        )

        return self.__parent__._cast(
            _7261.MountableComponentAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def oil_seal_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7262.OilSealAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7262,
        )

        return self.__parent__._cast(
            _7262.OilSealAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def part_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7263.PartAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7263,
        )

        return self.__parent__._cast(
            _7263.PartAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def part_to_part_shear_coupling_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7264.PartToPartShearCouplingAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7264,
        )

        return self.__parent__._cast(
            _7264.PartToPartShearCouplingAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def part_to_part_shear_coupling_half_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7266.PartToPartShearCouplingHalfAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7266,
        )

        return self.__parent__._cast(
            _7266.PartToPartShearCouplingHalfAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def planetary_gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7268.PlanetaryGearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7268,
        )

        return self.__parent__._cast(
            _7268.PlanetaryGearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def planet_carrier_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7269.PlanetCarrierAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7269,
        )

        return self.__parent__._cast(
            _7269.PlanetCarrierAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def point_load_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7270.PointLoadAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7270,
        )

        return self.__parent__._cast(
            _7270.PointLoadAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def power_load_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7271.PowerLoadAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7271,
        )

        return self.__parent__._cast(
            _7271.PowerLoadAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def pulley_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7272.PulleyAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7272,
        )

        return self.__parent__._cast(
            _7272.PulleyAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def ring_pins_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7273.RingPinsAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7273,
        )

        return self.__parent__._cast(
            _7273.RingPinsAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def rolling_ring_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7275.RollingRingAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7275,
        )

        return self.__parent__._cast(
            _7275.RollingRingAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def rolling_ring_assembly_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7276.RollingRingAssemblyAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7276,
        )

        return self.__parent__._cast(
            _7276.RollingRingAssemblyAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def root_assembly_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7278.RootAssemblyAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7278,
        )

        return self.__parent__._cast(
            _7278.RootAssemblyAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def shaft_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7279.ShaftAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7279,
        )

        return self.__parent__._cast(
            _7279.ShaftAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def shaft_hub_connection_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7280.ShaftHubConnectionAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7280,
        )

        return self.__parent__._cast(
            _7280.ShaftHubConnectionAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def specialised_assembly_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7282.SpecialisedAssemblyAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7282,
        )

        return self.__parent__._cast(
            _7282.SpecialisedAssemblyAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def spiral_bevel_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7283.SpiralBevelGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7283,
        )

        return self.__parent__._cast(
            _7283.SpiralBevelGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def spiral_bevel_gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7285.SpiralBevelGearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7285,
        )

        return self.__parent__._cast(
            _7285.SpiralBevelGearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def spring_damper_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7286.SpringDamperAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7286,
        )

        return self.__parent__._cast(
            _7286.SpringDamperAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def spring_damper_half_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7288.SpringDamperHalfAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7288,
        )

        return self.__parent__._cast(
            _7288.SpringDamperHalfAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def straight_bevel_diff_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7289.StraightBevelDiffGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7289,
        )

        return self.__parent__._cast(
            _7289.StraightBevelDiffGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def straight_bevel_diff_gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7291.StraightBevelDiffGearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7291,
        )

        return self.__parent__._cast(
            _7291.StraightBevelDiffGearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def straight_bevel_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7292.StraightBevelGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7292,
        )

        return self.__parent__._cast(
            _7292.StraightBevelGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def straight_bevel_gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7294.StraightBevelGearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7294,
        )

        return self.__parent__._cast(
            _7294.StraightBevelGearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def straight_bevel_planet_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7295.StraightBevelPlanetGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7295,
        )

        return self.__parent__._cast(
            _7295.StraightBevelPlanetGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def straight_bevel_sun_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7296.StraightBevelSunGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7296,
        )

        return self.__parent__._cast(
            _7296.StraightBevelSunGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def synchroniser_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7297.SynchroniserAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7297,
        )

        return self.__parent__._cast(
            _7297.SynchroniserAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def synchroniser_half_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7298.SynchroniserHalfAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7298,
        )

        return self.__parent__._cast(
            _7298.SynchroniserHalfAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def synchroniser_part_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7299.SynchroniserPartAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7299,
        )

        return self.__parent__._cast(
            _7299.SynchroniserPartAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def synchroniser_sleeve_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7300.SynchroniserSleeveAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7300,
        )

        return self.__parent__._cast(
            _7300.SynchroniserSleeveAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def torque_converter_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7301.TorqueConverterAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7301,
        )

        return self.__parent__._cast(
            _7301.TorqueConverterAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def torque_converter_pump_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7303.TorqueConverterPumpAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7303,
        )

        return self.__parent__._cast(
            _7303.TorqueConverterPumpAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def torque_converter_turbine_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7304.TorqueConverterTurbineAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7304,
        )

        return self.__parent__._cast(
            _7304.TorqueConverterTurbineAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def unbalanced_mass_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7305.UnbalancedMassAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7305,
        )

        return self.__parent__._cast(
            _7305.UnbalancedMassAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def virtual_component_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7306.VirtualComponentAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7306,
        )

        return self.__parent__._cast(
            _7306.VirtualComponentAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def worm_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7307.WormGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7307,
        )

        return self.__parent__._cast(
            _7307.WormGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def worm_gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7309.WormGearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7309,
        )

        return self.__parent__._cast(
            _7309.WormGearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def zerol_bevel_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7310.ZerolBevelGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7310,
        )

        return self.__parent__._cast(
            _7310.ZerolBevelGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def zerol_bevel_gear_set_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7312.ZerolBevelGearSetAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7312,
        )

        return self.__parent__._cast(
            _7312.ZerolBevelGearSetAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def abstract_assembly_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7444.AbstractAssemblyAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7444,
        )

        return self.__parent__._cast(_7444.AbstractAssemblyAdvancedSystemDeflection)

    @property
    def abstract_shaft_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7445.AbstractShaftAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7445,
        )

        return self.__parent__._cast(_7445.AbstractShaftAdvancedSystemDeflection)

    @property
    def abstract_shaft_or_housing_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7446.AbstractShaftOrHousingAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7446,
        )

        return self.__parent__._cast(
            _7446.AbstractShaftOrHousingAdvancedSystemDeflection
        )

    @property
    def agma_gleason_conical_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7451.AGMAGleasonConicalGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7451,
        )

        return self.__parent__._cast(
            _7451.AGMAGleasonConicalGearAdvancedSystemDeflection
        )

    @property
    def agma_gleason_conical_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7453.AGMAGleasonConicalGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7453,
        )

        return self.__parent__._cast(
            _7453.AGMAGleasonConicalGearSetAdvancedSystemDeflection
        )

    @property
    def assembly_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7454.AssemblyAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7454,
        )

        return self.__parent__._cast(_7454.AssemblyAdvancedSystemDeflection)

    @property
    def bearing_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7455.BearingAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7455,
        )

        return self.__parent__._cast(_7455.BearingAdvancedSystemDeflection)

    @property
    def belt_drive_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7457.BeltDriveAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7457,
        )

        return self.__parent__._cast(_7457.BeltDriveAdvancedSystemDeflection)

    @property
    def bevel_differential_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7458.BevelDifferentialGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7458,
        )

        return self.__parent__._cast(
            _7458.BevelDifferentialGearAdvancedSystemDeflection
        )

    @property
    def bevel_differential_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7460.BevelDifferentialGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7460,
        )

        return self.__parent__._cast(
            _7460.BevelDifferentialGearSetAdvancedSystemDeflection
        )

    @property
    def bevel_differential_planet_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7461.BevelDifferentialPlanetGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7461,
        )

        return self.__parent__._cast(
            _7461.BevelDifferentialPlanetGearAdvancedSystemDeflection
        )

    @property
    def bevel_differential_sun_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7462.BevelDifferentialSunGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7462,
        )

        return self.__parent__._cast(
            _7462.BevelDifferentialSunGearAdvancedSystemDeflection
        )

    @property
    def bevel_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7463.BevelGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7463,
        )

        return self.__parent__._cast(_7463.BevelGearAdvancedSystemDeflection)

    @property
    def bevel_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7465.BevelGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7465,
        )

        return self.__parent__._cast(_7465.BevelGearSetAdvancedSystemDeflection)

    @property
    def bolt_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7466.BoltAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7466,
        )

        return self.__parent__._cast(_7466.BoltAdvancedSystemDeflection)

    @property
    def bolted_joint_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7467.BoltedJointAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7467,
        )

        return self.__parent__._cast(_7467.BoltedJointAdvancedSystemDeflection)

    @property
    def clutch_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7468.ClutchAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7468,
        )

        return self.__parent__._cast(_7468.ClutchAdvancedSystemDeflection)

    @property
    def clutch_half_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7470.ClutchHalfAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7470,
        )

        return self.__parent__._cast(_7470.ClutchHalfAdvancedSystemDeflection)

    @property
    def component_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7472.ComponentAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7472,
        )

        return self.__parent__._cast(_7472.ComponentAdvancedSystemDeflection)

    @property
    def concept_coupling_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7473.ConceptCouplingAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7473,
        )

        return self.__parent__._cast(_7473.ConceptCouplingAdvancedSystemDeflection)

    @property
    def concept_coupling_half_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7475.ConceptCouplingHalfAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7475,
        )

        return self.__parent__._cast(_7475.ConceptCouplingHalfAdvancedSystemDeflection)

    @property
    def concept_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7476.ConceptGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7476,
        )

        return self.__parent__._cast(_7476.ConceptGearAdvancedSystemDeflection)

    @property
    def concept_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7478.ConceptGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7478,
        )

        return self.__parent__._cast(_7478.ConceptGearSetAdvancedSystemDeflection)

    @property
    def conical_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7479.ConicalGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7479,
        )

        return self.__parent__._cast(_7479.ConicalGearAdvancedSystemDeflection)

    @property
    def conical_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7481.ConicalGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7481,
        )

        return self.__parent__._cast(_7481.ConicalGearSetAdvancedSystemDeflection)

    @property
    def connector_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7483.ConnectorAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7483,
        )

        return self.__parent__._cast(_7483.ConnectorAdvancedSystemDeflection)

    @property
    def coupling_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7485.CouplingAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7485,
        )

        return self.__parent__._cast(_7485.CouplingAdvancedSystemDeflection)

    @property
    def coupling_half_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7487.CouplingHalfAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7487,
        )

        return self.__parent__._cast(_7487.CouplingHalfAdvancedSystemDeflection)

    @property
    def cvt_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7488.CVTAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7488,
        )

        return self.__parent__._cast(_7488.CVTAdvancedSystemDeflection)

    @property
    def cvt_pulley_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7490.CVTPulleyAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7490,
        )

        return self.__parent__._cast(_7490.CVTPulleyAdvancedSystemDeflection)

    @property
    def cycloidal_assembly_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7491.CycloidalAssemblyAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7491,
        )

        return self.__parent__._cast(_7491.CycloidalAssemblyAdvancedSystemDeflection)

    @property
    def cycloidal_disc_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7492.CycloidalDiscAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7492,
        )

        return self.__parent__._cast(_7492.CycloidalDiscAdvancedSystemDeflection)

    @property
    def cylindrical_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7495.CylindricalGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7495,
        )

        return self.__parent__._cast(_7495.CylindricalGearAdvancedSystemDeflection)

    @property
    def cylindrical_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7497.CylindricalGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7497,
        )

        return self.__parent__._cast(_7497.CylindricalGearSetAdvancedSystemDeflection)

    @property
    def cylindrical_planet_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7499.CylindricalPlanetGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7499,
        )

        return self.__parent__._cast(
            _7499.CylindricalPlanetGearAdvancedSystemDeflection
        )

    @property
    def datum_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7500.DatumAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7500,
        )

        return self.__parent__._cast(_7500.DatumAdvancedSystemDeflection)

    @property
    def external_cad_model_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7501.ExternalCADModelAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7501,
        )

        return self.__parent__._cast(_7501.ExternalCADModelAdvancedSystemDeflection)

    @property
    def face_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7502.FaceGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7502,
        )

        return self.__parent__._cast(_7502.FaceGearAdvancedSystemDeflection)

    @property
    def face_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7504.FaceGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7504,
        )

        return self.__parent__._cast(_7504.FaceGearSetAdvancedSystemDeflection)

    @property
    def fe_part_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7505.FEPartAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7505,
        )

        return self.__parent__._cast(_7505.FEPartAdvancedSystemDeflection)

    @property
    def flexible_pin_assembly_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7506.FlexiblePinAssemblyAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7506,
        )

        return self.__parent__._cast(_7506.FlexiblePinAssemblyAdvancedSystemDeflection)

    @property
    def gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7507.GearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7507,
        )

        return self.__parent__._cast(_7507.GearAdvancedSystemDeflection)

    @property
    def gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7509.GearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7509,
        )

        return self.__parent__._cast(_7509.GearSetAdvancedSystemDeflection)

    @property
    def guide_dxf_model_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7510.GuideDxfModelAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7510,
        )

        return self.__parent__._cast(_7510.GuideDxfModelAdvancedSystemDeflection)

    @property
    def hypoid_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7511.HypoidGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7511,
        )

        return self.__parent__._cast(_7511.HypoidGearAdvancedSystemDeflection)

    @property
    def hypoid_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7513.HypoidGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7513,
        )

        return self.__parent__._cast(_7513.HypoidGearSetAdvancedSystemDeflection)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7515.KlingelnbergCycloPalloidConicalGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7515,
        )

        return self.__parent__._cast(
            _7515.KlingelnbergCycloPalloidConicalGearAdvancedSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7517.KlingelnbergCycloPalloidConicalGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7517,
        )

        return self.__parent__._cast(
            _7517.KlingelnbergCycloPalloidConicalGearSetAdvancedSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7518.KlingelnbergCycloPalloidHypoidGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7518,
        )

        return self.__parent__._cast(
            _7518.KlingelnbergCycloPalloidHypoidGearAdvancedSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7520.KlingelnbergCycloPalloidHypoidGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7520,
        )

        return self.__parent__._cast(
            _7520.KlingelnbergCycloPalloidHypoidGearSetAdvancedSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7521.KlingelnbergCycloPalloidSpiralBevelGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7521,
        )

        return self.__parent__._cast(
            _7521.KlingelnbergCycloPalloidSpiralBevelGearAdvancedSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7523.KlingelnbergCycloPalloidSpiralBevelGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7523,
        )

        return self.__parent__._cast(
            _7523.KlingelnbergCycloPalloidSpiralBevelGearSetAdvancedSystemDeflection
        )

    @property
    def mass_disc_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7525.MassDiscAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7525,
        )

        return self.__parent__._cast(_7525.MassDiscAdvancedSystemDeflection)

    @property
    def measurement_component_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7526.MeasurementComponentAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7526,
        )

        return self.__parent__._cast(_7526.MeasurementComponentAdvancedSystemDeflection)

    @property
    def microphone_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7527.MicrophoneAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7527,
        )

        return self.__parent__._cast(_7527.MicrophoneAdvancedSystemDeflection)

    @property
    def microphone_array_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7528.MicrophoneArrayAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7528,
        )

        return self.__parent__._cast(_7528.MicrophoneArrayAdvancedSystemDeflection)

    @property
    def mountable_component_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7529.MountableComponentAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7529,
        )

        return self.__parent__._cast(_7529.MountableComponentAdvancedSystemDeflection)

    @property
    def oil_seal_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7530.OilSealAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7530,
        )

        return self.__parent__._cast(_7530.OilSealAdvancedSystemDeflection)

    @property
    def part_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7531.PartAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7531,
        )

        return self.__parent__._cast(_7531.PartAdvancedSystemDeflection)

    @property
    def part_to_part_shear_coupling_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7532.PartToPartShearCouplingAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7532,
        )

        return self.__parent__._cast(
            _7532.PartToPartShearCouplingAdvancedSystemDeflection
        )

    @property
    def part_to_part_shear_coupling_half_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7534.PartToPartShearCouplingHalfAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7534,
        )

        return self.__parent__._cast(
            _7534.PartToPartShearCouplingHalfAdvancedSystemDeflection
        )

    @property
    def planetary_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7536.PlanetaryGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7536,
        )

        return self.__parent__._cast(_7536.PlanetaryGearSetAdvancedSystemDeflection)

    @property
    def planet_carrier_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7537.PlanetCarrierAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7537,
        )

        return self.__parent__._cast(_7537.PlanetCarrierAdvancedSystemDeflection)

    @property
    def point_load_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7538.PointLoadAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7538,
        )

        return self.__parent__._cast(_7538.PointLoadAdvancedSystemDeflection)

    @property
    def power_load_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7539.PowerLoadAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7539,
        )

        return self.__parent__._cast(_7539.PowerLoadAdvancedSystemDeflection)

    @property
    def pulley_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7540.PulleyAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7540,
        )

        return self.__parent__._cast(_7540.PulleyAdvancedSystemDeflection)

    @property
    def ring_pins_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7541.RingPinsAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7541,
        )

        return self.__parent__._cast(_7541.RingPinsAdvancedSystemDeflection)

    @property
    def rolling_ring_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7543.RollingRingAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7543,
        )

        return self.__parent__._cast(_7543.RollingRingAdvancedSystemDeflection)

    @property
    def rolling_ring_assembly_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7544.RollingRingAssemblyAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7544,
        )

        return self.__parent__._cast(_7544.RollingRingAssemblyAdvancedSystemDeflection)

    @property
    def root_assembly_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7546.RootAssemblyAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7546,
        )

        return self.__parent__._cast(_7546.RootAssemblyAdvancedSystemDeflection)

    @property
    def shaft_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7547.ShaftAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7547,
        )

        return self.__parent__._cast(_7547.ShaftAdvancedSystemDeflection)

    @property
    def shaft_hub_connection_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7548.ShaftHubConnectionAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7548,
        )

        return self.__parent__._cast(_7548.ShaftHubConnectionAdvancedSystemDeflection)

    @property
    def specialised_assembly_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7550.SpecialisedAssemblyAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7550,
        )

        return self.__parent__._cast(_7550.SpecialisedAssemblyAdvancedSystemDeflection)

    @property
    def spiral_bevel_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7551.SpiralBevelGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7551,
        )

        return self.__parent__._cast(_7551.SpiralBevelGearAdvancedSystemDeflection)

    @property
    def spiral_bevel_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7553.SpiralBevelGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7553,
        )

        return self.__parent__._cast(_7553.SpiralBevelGearSetAdvancedSystemDeflection)

    @property
    def spring_damper_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7554.SpringDamperAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7554,
        )

        return self.__parent__._cast(_7554.SpringDamperAdvancedSystemDeflection)

    @property
    def spring_damper_half_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7556.SpringDamperHalfAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7556,
        )

        return self.__parent__._cast(_7556.SpringDamperHalfAdvancedSystemDeflection)

    @property
    def straight_bevel_diff_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7557.StraightBevelDiffGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7557,
        )

        return self.__parent__._cast(
            _7557.StraightBevelDiffGearAdvancedSystemDeflection
        )

    @property
    def straight_bevel_diff_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7559.StraightBevelDiffGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7559,
        )

        return self.__parent__._cast(
            _7559.StraightBevelDiffGearSetAdvancedSystemDeflection
        )

    @property
    def straight_bevel_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7560.StraightBevelGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7560,
        )

        return self.__parent__._cast(_7560.StraightBevelGearAdvancedSystemDeflection)

    @property
    def straight_bevel_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7562.StraightBevelGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7562,
        )

        return self.__parent__._cast(_7562.StraightBevelGearSetAdvancedSystemDeflection)

    @property
    def straight_bevel_planet_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7563.StraightBevelPlanetGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7563,
        )

        return self.__parent__._cast(
            _7563.StraightBevelPlanetGearAdvancedSystemDeflection
        )

    @property
    def straight_bevel_sun_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7564.StraightBevelSunGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7564,
        )

        return self.__parent__._cast(_7564.StraightBevelSunGearAdvancedSystemDeflection)

    @property
    def synchroniser_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7565.SynchroniserAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7565,
        )

        return self.__parent__._cast(_7565.SynchroniserAdvancedSystemDeflection)

    @property
    def synchroniser_half_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7566.SynchroniserHalfAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7566,
        )

        return self.__parent__._cast(_7566.SynchroniserHalfAdvancedSystemDeflection)

    @property
    def synchroniser_part_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7567.SynchroniserPartAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7567,
        )

        return self.__parent__._cast(_7567.SynchroniserPartAdvancedSystemDeflection)

    @property
    def synchroniser_sleeve_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7568.SynchroniserSleeveAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7568,
        )

        return self.__parent__._cast(_7568.SynchroniserSleeveAdvancedSystemDeflection)

    @property
    def torque_converter_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7569.TorqueConverterAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7569,
        )

        return self.__parent__._cast(_7569.TorqueConverterAdvancedSystemDeflection)

    @property
    def torque_converter_pump_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7571.TorqueConverterPumpAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7571,
        )

        return self.__parent__._cast(_7571.TorqueConverterPumpAdvancedSystemDeflection)

    @property
    def torque_converter_turbine_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7572.TorqueConverterTurbineAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7572,
        )

        return self.__parent__._cast(
            _7572.TorqueConverterTurbineAdvancedSystemDeflection
        )

    @property
    def unbalanced_mass_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7574.UnbalancedMassAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7574,
        )

        return self.__parent__._cast(_7574.UnbalancedMassAdvancedSystemDeflection)

    @property
    def virtual_component_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7575.VirtualComponentAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7575,
        )

        return self.__parent__._cast(_7575.VirtualComponentAdvancedSystemDeflection)

    @property
    def worm_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7576.WormGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7576,
        )

        return self.__parent__._cast(_7576.WormGearAdvancedSystemDeflection)

    @property
    def worm_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7578.WormGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7578,
        )

        return self.__parent__._cast(_7578.WormGearSetAdvancedSystemDeflection)

    @property
    def zerol_bevel_gear_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7579.ZerolBevelGearAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7579,
        )

        return self.__parent__._cast(_7579.ZerolBevelGearAdvancedSystemDeflection)

    @property
    def zerol_bevel_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7581.ZerolBevelGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7581,
        )

        return self.__parent__._cast(_7581.ZerolBevelGearSetAdvancedSystemDeflection)

    @property
    def part_fe_analysis(self: "CastSelf") -> "_7943.PartFEAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7943,
        )

        return self.__parent__._cast(_7943.PartFEAnalysis)

    @property
    def part_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7944.PartStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7944,
        )

        return self.__parent__._cast(_7944.PartStaticLoadAnalysisCase)

    @property
    def part_time_series_load_analysis_case(
        self: "CastSelf",
    ) -> "_7945.PartTimeSeriesLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7945,
        )

        return self.__parent__._cast(_7945.PartTimeSeriesLoadAnalysisCase)

    @property
    def part_analysis_case(self: "CastSelf") -> "PartAnalysisCase":
        return self.__parent__

    def __getattr__(self: "CastSelf", name: str) -> "Any":
        try:
            return self.__getattribute__(name)
        except AttributeError:
            class_name = utility.camel(name)
            raise CastException(
                f'Detected an invalid cast. Cannot cast to type "{class_name}"'
            ) from None


@extended_dataclass(frozen=True, slots=True, weakref_slot=True, eq=False)
class PartAnalysisCase(_2949.PartAnalysis):
    """PartAnalysisCase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PART_ANALYSIS_CASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def three_d_isometric_view(self: "Self") -> "Image":
        """Image

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ThreeDIsometricView")

        if temp is None:
            return None

        value = conversion.pn_to_mp_smt_bitmap(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def three_d_view(self: "Self") -> "Image":
        """Image

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ThreeDView")

        if temp is None:
            return None

        value = conversion.pn_to_mp_smt_bitmap(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def three_d_view_orientated_in_xy_plane_with_z_axis_pointing_into_the_screen(
        self: "Self",
    ) -> "Image":
        """Image

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ThreeDViewOrientatedInXyPlaneWithZAxisPointingIntoTheScreen"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_smt_bitmap(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def three_d_view_orientated_in_xy_plane_with_z_axis_pointing_out_of_the_screen(
        self: "Self",
    ) -> "Image":
        """Image

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ThreeDViewOrientatedInXyPlaneWithZAxisPointingOutOfTheScreen"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_smt_bitmap(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def three_d_view_orientated_in_xz_plane_with_y_axis_pointing_into_the_screen(
        self: "Self",
    ) -> "Image":
        """Image

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ThreeDViewOrientatedInXzPlaneWithYAxisPointingIntoTheScreen"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_smt_bitmap(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def three_d_view_orientated_in_xz_plane_with_y_axis_pointing_out_of_the_screen(
        self: "Self",
    ) -> "Image":
        """Image

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ThreeDViewOrientatedInXzPlaneWithYAxisPointingOutOfTheScreen"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_smt_bitmap(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def three_d_view_orientated_in_yz_plane_with_x_axis_pointing_into_the_screen(
        self: "Self",
    ) -> "Image":
        """Image

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ThreeDViewOrientatedInYzPlaneWithXAxisPointingIntoTheScreen"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_smt_bitmap(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def three_d_view_orientated_in_yz_plane_with_x_axis_pointing_out_of_the_screen(
        self: "Self",
    ) -> "Image":
        """Image

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ThreeDViewOrientatedInYzPlaneWithXAxisPointingOutOfTheScreen"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_smt_bitmap(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_PartAnalysisCase":
        """Cast to another type.

        Returns:
            _Cast_PartAnalysisCase
        """
        return _Cast_PartAnalysisCase(self)
