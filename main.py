import requests
import pandas as pd
import json
import time


# 获取某一mod所有的文件列表并以数据框返回
def get_files(modid):
    headers = {
        'Accept': 'application/json',
        'x-api-key': '$2a$10$LhtoxmW9RQT3gXvSQDgXZuTRAwXKzZMlzcY0CKj5LNVC7o61en7ga'
    }
    url = 'https://api.curseforge.com/v1/mods/' + modid + '/files'
    r = requests.get(url, headers=headers)
    r_meta = r.json()

    files_meta = pd.DataFrame(columns=['fileID', 'fileDate', 'modloader', 'MCVersions', 'downloadUrl'])
    for i in range(len(r_meta['data'])):
        gameVersions = r_meta['data'][i]['gameVersions']
        MCVers = []
        modloader = 'Forge'  # 认为modloader默认为Forge，待进一步确定
        for j in range(len(gameVersions)):
            if gameVersions[j] == 'Fabric':
                modloader = 'Fabric'
            elif gameVersions[j] == 'Forge':
                modloader = 'Forge'
            elif gameVersions[j] == 'Rift':
                modloader = 'Rift'
            else:
                MCVers.append(gameVersions[j])

        meta_i = pd.DataFrame({'fileID': r_meta['data'][i]['id'],
                               'fileDate': r_meta['data'][i]['fileDate'],
                               'modloader': modloader,
                               'MCVersions': MCVers,
                               'downloadUrl': r_meta['data'][i]['downloadUrl']})
        files_meta = files_meta.append(meta_i)

    return files_meta


# 根据需求从数据框中返回下载Url
def get_newest(files_meta, loader, gver):
    meta_select = files_meta.loc[files_meta['modloader'] == loader, ]
    meta_select = meta_select.loc[meta_select['MCVersions'] == gver, ]
    newest = meta_select.loc[meta_select['fileDate'] == meta_select.loc[:, 'fileDate'].max()]
    return newest


def main():
    with open('./config.json') as config_meta:
        config = json.load(config_meta)
    gamever = config['MC_Version']
    modloader = config['Mod_Loader']
    modids = config['ModIDs']
    d_urls = []

    try:
        with open('./modlist.json') as modlist:
            mods = json.load(modlist)
        first = False
    except:
        mods = {}
        first = True

# 根config中的modids获取最新的文件url
    note = {}
    if first:
        # 第一次运行则下载所有mods并将modid与fileid写入modlist
        for i in range(len(modids)):
            modid = modids[i]
            files_meta = get_files(modid)
            new = get_newest(files_meta, modloader, gamever)
            file_id = new.at[0, 'fileID']
            note[modid] = [str(file_id)]
            d_url = new.at[0, 'downloadUrl']
            d_urls.append(d_url)
    else:
        # 不是第一次则在mods中modid列表第0位写入新的fileid，旧的写入第1位
        with open('./latest.json', 'w') as lastjson:
            last = json.load(lastjson)
        for i in range(len(modids)):
            modid = modids[i]
            files_meta = get_files(modid)
            new = get_newest(files_meta, modloader, gamever)
            file_id = new.at[0, 'fileID']
            old_file = last[modid][0]
            if int(old_file) < file_id:
                note[modid][1] = old_file
                note[modid][0] = str(file_id)
                d_url = new.at[0, 'downloadUrl']
                d_urls.append(d_url)
    datetag = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    mods[datetag] = note
    with open('./latest.json', 'w') as latest:
        latest.write(json.dumps(note))
    with open('./modlist.json', 'w') as modlist:
        modlist.write(json.dumps(mods))
    with open('./download_urls.txt', 'w') as download_urls:
        for urls in d_urls:
            download_urls.write(urls+'\n')


if __name__ == '__main__':
    main()
