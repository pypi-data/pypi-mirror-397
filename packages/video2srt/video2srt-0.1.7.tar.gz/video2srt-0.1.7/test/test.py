#%%
import sys
sys.path.append("e:/OK_Blue/")

#%%
from video2srt import video_to_srt, hello_video2srt, sample

#%%
from video2srt import hello_video2srt

hello_video2srt()

#%%
# 运行示例(sample)
import sys
sys.path.append("e:/OK_Blue/")
from video2srt import sample
sample()

#%%

import sys
sys.path.append("e:/OK_Blue/")
from video2srt import video_to_srt

# ## 配置参数（Parameters Configuration）

VIDEO_PATH = input("Please input video file path:")  
# 视频文件路径
SRT_OUTPUT = "test_out.srt"  
# 输出SRT路径
MODEL_SIZE = "base"  
# Whisper模型类型（tiny/base/small/medium/large）
# 默认使用base, large精度更高，需更多显存，处理时间更长，支持小众语言和方言
LANGUAGE = "zh"      
# 识别语言，默认自动识别, 支持多语言（90多种）识别（如en/zh/ja/lo/fr/de等, 更多语言请参考Whisper文档）
IS_TRANSLATE = True 
# 是否翻译识别的文本，默认不翻译
TRANSLATE_ENGINE = "model"  
# 翻译引擎（model/api），model默认使用本地模型facebook/m2m100_418M，api默认使用Google翻译API
TRANSLATE_LANG = "en"      
# 翻译目标语言（如zh/en/ja/ko/fr）, 默认翻译为中文，支持100+种语言翻译，j基本与whisper一致，但有一些差异,如没有对方言的支持（zh/yue/wuu->zh)，系统会自动将其转换为zh
USE_GPU = True     
# 是否使用GPU加速，默认会自动检测是否有可用的GPU，若有则使用GPU加速，否则使用CPU

# ## 生成SRT（使用video_to_srt函数）
srt_lines = video_to_srt(
    video_path = VIDEO_PATH,
    srt_output_path = SRT_OUTPUT,
    model_size = MODEL_SIZE,
    language = LANGUAGE,
    is_translate = IS_TRANSLATE,
    translate_engine = TRANSLATE_ENGINE,
    translate_lang = TRANSLATE_LANG,
    use_gpu = USE_GPU
)

print("Sample SRT 0-7 lines:")
print("\n".join(srt_lines[:7]))
# %%
