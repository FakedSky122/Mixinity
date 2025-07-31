import wave
import audioop

#info
version = '1.4-English'
print('Mixinity v'+version)
file = input('Open file\nfile name：')
with wave.open(file, 'rb') as wav:
    print('\nfile info：')
    info = wav.getparams()
    nchannels, sampwidth, framerate, nframes, comptype, compname = info
    print("Channels:", nchannels)
    print("Sample width(Bytes):", sampwidth)
    print("Sample rate(Hz):", framerate)
    print("Frames:", nframes)
    print("Compress type:", comptype)
    print("Compress info:", compname)
    print('Bit depth：',sampwidth*8,'Bit')
    filelen = round(nframes / framerate * 10) / 10
    print('Duration:',filelen,'s')
    size = nframes * sampwidth * nchannels / 1024 / 1024
    print('Size：',round(size*100)/100,'MiB')
    data = wav.readframes(info.nframes)
while True:
    cho = input('\n[F]File [E]Effects [C]Cut [S]Stereo Mix [A]About [Q]Quit\n> ')
    
    if cho == 'f' or cho == 'F':
        inp = input('\n[I]File info\n[S]Save file\n> ')
    elif cho == 'e' or cho == 'E':
        inp = input('\n[A]Loudness \n[T]Tone/speed\n[D]Delay/reverberation\n[L]Low-pass filter\n[H]High-pass filter\n[R]Reverse\n[I]Phase reverse\n[F]Edit sample rate\n[W]Edit bit depth\n> ')
    elif cho == 'c' or cho == 'C':
        cut_start = float(input('Start time（s）：'))
        cut_end = float(input('End time（s）：'))
        cut_start = round(cut_start * sampwidth * nchannels * framerate)
        if cut_end == -1:
            cut_end = -1
        else:
            cut_end = round(cut_end * sampwidth * nchannels * framerate)
        data = data[cut_start:cut_end]
        continue;
    elif cho == 's' or cho == 'S':
        inp = input('\n[M]To mono\n[S]To stereo\n[P]Phase\n> ')
    elif cho == 'a' or cho == 'A':
        print('\nMixinity v'+version,'by FakedSky122')
        continue;
    elif cho == 'q' or cho == 'Q':
        quit()
    #处理/效果项
    if inp == 'a' or inp == 'A':
        #响度
        mulinp = float(input('Loudness change（dB）：'))
        mulinp = 10**(mulinp/20) #换算声压级
        data = audioop.mul(data, sampwidth, mulinp)
    
    elif inp == 't' or inp == 'T':
        #速度（变调）
        speedinp = input('Tone/speed change(~:speed,~t:tone)：')
        if 't' in speedinp:
            mul = 1.0595 #半音的频率音程（ 2^(1/12),近似 ）
            speedinp = mul ** float(str(speedinp).replace('t','')) # ** = ^（幂运算）
        else:
            speedinp = float(speedinp)
        framerate = int(framerate*speedinp)
    
    elif inp == 'd' or inp == 'D':
        #delay、混响
        delayinp = int(input('Delay/reverberation effect：time(ms)：'))
        damprate = float(input('Delay/reverberation effect：reflect[0 No reflect ~ 1 All reflect]：'))
        silence = b'\x00'*int((sampwidth * nchannels * framerate * delayinp / 1000)) #计算延时时间
        delayed = silence + data #开头添加静音
        data = data + silence #对齐长度
        delayed = audioop.mul(delayed, sampwidth, damprate) #衰减
        data = audioop.add(data, delayed, sampwidth) #叠加
    
    elif inp == 's' or inp == 'S':
        if cho == 'f' or cho == 'F':
            #保存
            with wave.open('output.wav', 'wb') as out:
                out.setnchannels(nchannels)  # 设置声道数
                out.setsampwidth(2)  # 设置采样宽度（字节数）
                out.setframerate(framerate)  # 设置采样率
                out.setnframes(0)  # 设置帧数
                out.writeframes(data)
                out.close()
                print('Succeeded')
        elif cho == 's' or cho == 'S':
            lfactor = float(input('left factor（default 0.5）：'))
            rfactor = float(input('right factor（default 0.5）：'))
            data = audioop.tostereo(data, sampwidth, lfactor , rfactor)
            if nchannels == 2:
                framerate = framerate * 2
            nchannels = 2
   
    elif inp == 'm' or inp == 'M':
        data = audioop.tomono(data, sampwidth, 0.5, 0.5)
        nchannels = 1
    
    elif inp == 'i' or inp == 'I':
        if cho == 'f' or cho == 'F':
            print('\nfile info：')
            print("Channels:", nchannels)
            print("Sample width(Bytes):", sampwidth)
            print("Sample rate(Hz):", framerate)
            print("Frames:", nframes)
            print("Compress type:", comptype)
            print("Compress info:", compname)
            print('Bit depth：',sampwidth*8,'Bit')
            filelen = round(nframes / framerate * 10) / 10
            print('Duration:',filelen,'s')
            size = nframes * sampwidth * nchannels / 1024 / 1024
            print('Size：',round(size*100)/100,'MiB')
        elif cho == 'i' or cho == 'I':
            data = data = audioop.mul(data, sampwidth, -1)

    elif inp == 'p' or inp == 'P':
        method = input('[1]Edit by loudness [2]Edit by direction：')
        if method == '1':
            lfactor = float(input('left factor（default 0.5）：'))
            rfactor = float(input('right factor（default 0.5）：'))
            data = audioop.tomono(data, sampwidth, 0.5, 0.5)
        elif method == '2':
            phase = float(input('Phase（left -100，middle 0，right 100）：'))
            rfactor = (phase + 100) / 200
            lfactor = 1 - rfactor
            data = audioop.tomono(data, sampwidth, lfactor, rfactor)
        else:
            data = audioop.tomono(data, sampwidth, 0.5, 0.5)
        data = audioop.tostereo(data, sampwidth, lfactor , rfactor)

    elif inp == 'f' or inp == 'F':
        new_rate = int(input('new sample rate(Hz)：'))
        data, state = audioop.ratecv(data, sampwidth, nchannels, framerate, new_rate, None)
        framerate = new_rate

    elif inp == 'w' or inp == 'W':
        new_bitdepth = int(input('new bit depth(bit)：'))
        sampwidth = round(new_bitdepth/8)

    elif inp == 'l' or inp == 'L':
        end_rate = int(input('end rate(Hz)：')) * 10
        high_cut, state = audioop.ratecv(data, sampwidth, nchannels, framerate, end_rate, None) #完全高切
        high_cut, state = audioop.ratecv(high_cut, sampwidth, nchannels, end_rate, framerate, None)
        min_len = min(len(data), len(high_cut)) #确保长度一致
        data = audioop.mul(data, sampwidth, 0.5)
        high_cut = audioop.mul(high_cut, sampwidth, 0.5)
        data = audioop.add(data[:min_len], high_cut[:min_len], sampwidth) #叠加原音频与高切音频
    
    elif inp == 'h' or inp == 'H':
        end_rate = int(input('end rate(Hz)：')) * 10
        high_cut, state = audioop.ratecv(data, sampwidth, nchannels, framerate, end_rate, None) #完全高切
        high_cut, state = audioop.ratecv(high_cut, sampwidth, nchannels, end_rate, framerate, None)
        min_len = min(len(data), len(high_cut)) #确保长度一致
        data = audioop.mul(data, sampwidth, 0.5)
        high_cut = audioop.mul(high_cut, sampwidth, -0.5) # 负数将低音反向
        data = audioop.add(data[:min_len], high_cut[:min_len], sampwidth) #叠加原音频与高切的反相音频

    elif inp == 'r' or inp == 'R':
        data = audioop.reverse(data, sampwidth)
