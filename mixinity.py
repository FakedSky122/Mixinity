import wave
import audioop
import struct
import winsound

#info
version = '1.5'
print('Mixinity v'+version)
file = input('打开文件\n文件名：')
with wave.open(file, 'rb') as wav:
    print('\n文件信息：')
    info = wav.getparams()
    nchannels, sampwidth, framerate, nframes, comptype, compname = info
    print("声道数:", nchannels)
    print("采样宽度(字节):", sampwidth)
    print("采样率(Hz):", framerate)
    print("总帧数:", nframes)
    print("压缩类型:", comptype)
    print("压缩说明:", compname)
    print('位深度：',sampwidth*8,'Bit')
    filelen = round(nframes / framerate * 10) / 10
    print('持续时长(该项无法实时改变):',filelen,'秒')
    size = nframes * sampwidth * nchannels / 1024 / 1024
    #code_rate = nframes * sampwidth * nchannels / (nframes / framerate)
    code_rate = sampwidth * nchannels * framerate / 125
    print('文件大小：',round(size*100)/100,'MiB')
    data = wav.readframes(info.nframes)
    print('码率：',code_rate,'kbps')

while True:
    cho = input('\n[F]文件 [E]效果 [C]剪辑 [S]立体声混音 [A]关于 [Q]退出\n> ')
    
    if cho == 'f' or cho == 'F':
        inp = input('\n[I]文件信息\n[S]保存\n[P]预览\n[C]叠加文件\n> ')
    elif cho == 'e' or cho == 'E':
        inp = input('\n[A]响度\n[T]音高/速度\n[D]Delay/混响\n[L]低通滤波器\n[H]高通滤波器\n[R]倒放\n[I]反相(波形反转)\n[O]过载/失真\n[F]调整采样率\n[W]调整位深度\n> ')
    elif cho == 'c' or cho == 'C':
        cut_start = float(input('剪裁开始时间（秒，0为不设置）：'))
        cut_end = float(input('剪裁结束时间（秒，-1为不设置）：'))
        cut_start = round(cut_start * sampwidth * nchannels * framerate)
        if cut_end == -1:
            cut_end = -1
        else:
            cut_end = round(cut_end * sampwidth * nchannels * framerate)
        data = data[cut_start:cut_end]
        continue;
    elif cho == 's' or cho == 'S':
        inp = input('\n[M]立体声转单声道\n[S]单声道转立体声\n[P]立体声相位\n[C]中置声道提取（提取伴奏）\n> ')
    elif cho == 'a' or cho == 'A':
        print('\nMixinity v'+version,'by FakedSky122')
        continue;
    elif cho == 'q' or cho == 'Q':
        quit()
    #处理/效果项
    if inp == 'a' or inp == 'A':
        #响度
        mulinp = float(input('响度调整（dB）：'))
        mulinp = 10**(mulinp/20) #换算声压级
        data = audioop.mul(data, sampwidth, mulinp)
    
    elif inp == 't' or inp == 'T':
        #速度（变调）
        speedinp = input('速度/音高调整(~:倍速,~t:半音)：')
        if 't' in speedinp:
            mul = 1.0595 #半音的频率音程（ 2^(1/12),近似 ）
            speedinp = mul ** float(str(speedinp).replace('t','')) # ** = ^（幂运算）
        else:
            speedinp = float(speedinp)
        framerate = int(framerate*speedinp)
    
    elif inp == 'd' or inp == 'D':
        #delay、混响
        delayinp = int(input('delay/混响效果：时间(ms)：'))
        damprate = float(input('delay/混响效果：衰减率[0 完全衰减 ~ 1 不衰减]：'))
        silence = b'\x00'*int((sampwidth * nchannels * framerate * delayinp / 1000)) #计算延时时间
        delayed = silence + data #开头添加静音
        data = data + silence #对齐长度
        delayed = audioop.mul(delayed, sampwidth, damprate) #衰减
        data = audioop.add(data, delayed, sampwidth) #叠加
    
    elif inp == 's' or inp == 'S':
        if cho == 'f' or cho == 'F':
            #保存
            outputName = file.split('.')[0] + ' output.wav'
            with wave.open(outputName, 'wb') as out:
                out.setnchannels(nchannels)  # 设置声道数
                out.setsampwidth(sampwidth)  # 设置采样宽度（字节数）
                out.setframerate(framerate)  # 设置采样率
                out.setnframes(0)  # 设置帧数
                out.writeframes(data)
                out.close()
                print('保存成功')
        elif cho == 's' or cho == 'S':
            lfactor = float(input('左声道音量（默认为0.5）：'))
            rfactor = float(input('右声道音量（默认为0.5）：'))
            data = audioop.tostereo(data, sampwidth, lfactor , rfactor)
            if nchannels == 2:
                framerate = framerate * 2
            nchannels = 2
   
    elif inp == 'm' or inp == 'M':
        lfactor = float(input('左声道音量（0:不提取左声道，1：只提取左声道）：'))
        rfactor = float(input('右声道音量（0:不提取右声道，1：只提取右声道）：'))
        data = audioop.tomono(data, sampwidth, lfactor, rfactor)
        nchannels = 1
    
    elif inp == 'i' or inp == 'I':
        if cho == 'f' or cho == 'F':
            print('\n文件：'+file)
            print("声道数:", nchannels)
            print("采样宽度(字节):", sampwidth)
            print("采样率(Hz):", framerate)
            print("总帧数:", nframes)
            print("压缩类型:", comptype)
            print("压缩说明:", compname)
            print('位深度：',sampwidth*8,'Bit')
            filelen = round(nframes / framerate * 10) / 10
            print('持续时长(该项无法实时改变):',filelen,'秒')
            size = nframes * sampwidth * nchannels / 1024 / 1024
            print('文件大小：',round(size*100)/100,'MiB')
            code_rate = sampwidth * nchannels * framerate / 125
            print('码率：',code_rate,'kbps')
        elif cho == 'i' or cho == 'I':
            data = data = audioop.mul(data, sampwidth, -1)

    elif inp == 'p' or inp == 'P':
        if cho == 's' or cho == 'S':
            print('（该功能会使实际的立体声宽度为0）')
            method = input('[1]按声道音量调整 [2]按相位左右调整：')
            if method == '1':
                lfactor = float(input('左声道音量（默认为0.5）：'))
                rfactor = float(input('右声道音量（默认为0.5）：'))
                data = audioop.tomono(data, sampwidth, 0.5, 0.5)
            elif method == '2':
                phase = float(input('音频相位（最左为-100，默认为0，最右为100）：'))
                rfactor = (phase + 100) / 200
                lfactor = 1 - rfactor
                data = audioop.tomono(data, sampwidth, lfactor, rfactor)
            else:
                data = audioop.tomono(data, sampwidth, 0.5, 0.5)
            data = audioop.tostereo(data, sampwidth, lfactor , rfactor)
        elif cho == 'f' or cho == 'F':
            with wave.open('buffer.wav', 'wb') as out:
                out.setnchannels(nchannels)  # 设置声道数
                out.setsampwidth(sampwidth)  # 设置采样宽度（字节数）
                out.setframerate(framerate)  # 设置采样率
                out.setnframes(0)  # 设置帧数
                lenbuffer = sampwidth * nchannels * framerate * 5
                buffer = data[:lenbuffer]
                out.writeframes(buffer)
                out.close()
                print('缓存成功（5秒）')
            winsound.PlaySound('buffer.wav', winsound.SND_FILENAME)
            
    elif inp == 'f' or inp == 'F':
        new_rate = int(input('新采样率(Hz)：'))
        data, state = audioop.ratecv(data, sampwidth, nchannels, framerate, new_rate, None)
        framerate = new_rate

    elif inp == 'w' or inp == 'W':
        new_bitdepth = int(input('新位深度(bit)：'))
        if new_bitdepth == 8:
            # 原始数据是 16-bit（2 字节）整型
            samples = list(struct.unpack('<' + 'h' * (len(data) // 2), data))  # 'h' = signed 16-bit
            # 将 16-bit [-32768, 32767] 映射到 （x bit [0,2^x-1]）8-bit [0, 255]
            new_samples = [(s + 32768) // 256 for s in samples]  # 简单线性缩放 + 截断
            data = struct.pack('<' + 'B' * len(new_samples), *new_samples)  # 'B' = unsigned 8-bit
            sampwidth = 1
        else:
            sampwidth = round(new_bitdepth/8)
        
        if sampwidth < 1:
            sampwidth = 1

    elif inp == 'l' or inp == 'L':
        end_rate = int(input('截止频率(Hz)：')) * 10
        high_cut, state = audioop.ratecv(data, sampwidth, nchannels, framerate, end_rate, None) #完全高切
        high_cut, state = audioop.ratecv(high_cut, sampwidth, nchannels, end_rate, framerate, None)
        min_len = min(len(data), len(high_cut)) #确保长度一致
        data = audioop.mul(data, sampwidth, 0.5)
        high_cut = audioop.mul(high_cut, sampwidth, 0.5)
        data = audioop.add(data[:min_len], high_cut[:min_len], sampwidth) #叠加原音频与高切音频
    
    elif inp == 'h' or inp == 'H':
        end_rate = int(input('截止频率(Hz)：')) * 10
        high_cut, state = audioop.ratecv(data, sampwidth, nchannels, framerate, end_rate, None) #完全高切
        high_cut, state = audioop.ratecv(high_cut, sampwidth, nchannels, end_rate, framerate, None)
        min_len = min(len(data), len(high_cut)) #确保长度一致
        data = audioop.mul(data, sampwidth, 1)
        high_cut = audioop.mul(high_cut, sampwidth, -0.5) # 负数将低音反向
        data = audioop.add(data[:min_len], high_cut[:min_len], sampwidth) #叠加原音频与高切的反相音频

    elif inp == 'r' or inp == 'R':
        data = audioop.reverse(data, sampwidth)

    elif inp == 'o' or inp == 'O':
        dist_range = 1.3**float(input('过载/失真幅度（0~10）：'))
        if dist_range > 1.3**10:
            dist_range = 1.3**10
        data = audioop.mul(data, sampwidth, dist_range)
        data = audioop.mul(data, sampwidth, 1.5/dist_range)
    
    elif inp == 'c' or inp == 'C':
        if cho == 's' or cho == 'S':
            lefts = audioop.tomono(data, sampwidth, 1, 0) #提取左声道
            rights = audioop.tomono(data, sampwidth, 0, -1) #提取右声道（反相）
            data = audioop.add(lefts, rights, sampwidth) #叠加
            data = audioop.mul(data, sampwidth, 1.5)
            nchannels = 1
        elif cho == 'f' or cho == 'F':
            cover_file = input('打开叠加的文件\n文件名：')
            with wave.open(cover_file, 'rb') as cover_wav:
                cover_info = cover_wav.getparams()
                #nchannels, sampwidth, framerate, nframes, comptype, compname = info
                cover_nchannels, cover_sampwidth, cover_framerate, cover_nframes, cover_comptype, cover_compname  = cover_info
                cover = cover_wav.readframes(cover_nframes)
            data_factor = float(input('混合强度（当前文件）：'))
            cover_factor = float(input('混合强度（叠加文件）：'))
            data = audioop.mul(data, sampwidth, data_factor)
            cover = audioop.mul(cover, cover_sampwidth, cover_factor)
            min_len = min(len(data), len(cover)) #确保长度一致
            data = audioop.add(data[:min_len], cover[:min_len], sampwidth)
            file = file.split('.')[0] + ' + ' + cover_file
