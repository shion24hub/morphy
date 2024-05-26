# Morphy CLI

## Simple Examples

### 1. Update
To add Bybit BTCUSDT data from January 1 to 3, 2024 to the data storage,
```console
$ morphy update item bybit BTCUSDT 20240101 20240103
Downloading... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:10
All processes are completed.
Elapsed time: 10.84 sec
```

### 2. Make
To save to 3600-sec OHLCV data in the current directory,
```console
$ morphy make item bybit BTCUSDT 20240101 20240103 3600
Making... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
All processes are completed.
Elapsed time: 0.24 sec
$ ls
bybit_BTCUSDT_20240101_20240103_3600s.csv.gz 
```

### 3. Show
To check the symbols already stored,
``` console
$ morphy show items
Total size: 2.85 MB

Exchange   Symbol     Begin      End       
bybit      BTCUSDT    20240101   20240103  
```

### 4. Remove
To remove symbol data that is no longer needed, specifying a date,
``` console
$ morphy remove item bybit BTCUSDT 20240101 20240102
[ Confirm ]
Do you really want to remove 20240101 - 20240102 data for BTCUSDT? (y/n): y
All processes are completed.
$ morphy show items
Total size: 1.01 MB

Exchange   Symbol     Begin      End       
bybit      BTCUSDT    20240103   20240103  
```

## How to delete
If for some reason you want to delete all data related to morphy, delete the `$HOME/.morphy` directory completely. If you have changed the storage directory, delete that directory separately as well. 

``` console
$ cd
$ rm -rf .morphy/
```