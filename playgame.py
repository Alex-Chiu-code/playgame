import os, sys, random
import time

import pygame 
from pygame.locals import*



class Box(object):  # 定義class Box，處理概念轉圖像的方格繪製
    #-------------------------------------------------------------------------
    # 建構式
    #   pygame    : pygame
    #   canvas    : 畫布
    #   name      : 物件名稱
    #   rect      : 位置、大小 (X,Y,長,寬)
    #   color     : 顏色
    #-------------------------------------------------------------------------
    def __init__( self, pygame, canvas, name, rect, color):
        self.pygame = pygame
        self.canvas = canvas
        self.name = name
        self.rect = rect
        self.color = color

        self.visible = True # 允許繪製
        

    def update(self):   # 定義把藍圖概念轉至畫布的 method
        if(self.visible):
            self.pygame.draw.rect( self.canvas, self.color, self.rect)  # 繪製方格
#=======================================================================================

BRICK_DROP_PERIOD   = 0.01  # normal drop speed
BRICK_DOWN_SPEED_MAX = 0.5  # speed when press down

# 先定義顏色，方便後面顏色表現的處理
color_block         = (0,0,0)
color_white         = (255, 255, 255)
color_red           = (255, 0, 0)
color_green         = (0,255,0)
color_blue          = (0,0,255)
color_yellow        = (255,255,0)
color_pink          = (255,0,255)
color_sky_blue      = (0,255,255)
color_orange        = (255,128,0)
color_dark_blue     = (72,72,147)
color_purple        = (145,70,136)
color_gray          = (107,130,114)
color_gray_block    = (20,31,23)
tab_color1 = [color_block, color_blue, color_green, color_sky_blue, color_red, color_pink, color_yellow, color_white, color_block]
tab_color2 = [color_block, color_red, color_orange, color_yellow, color_green, color_blue, color_dark_blue, color_purple, color_block]
# 做色盤，方便更替遊戲整體顏色
tab_color = tab_color2

# 定義視窗
canvas_width = 470
canvas_height = 600
WND_RECT = [0, 0, canvas_width, canvas_height]
GAME_AREA =  [ 5, 20, 280, 560]
GAME_AREA_BORDER =  [ GAME_AREA[0]-2, GAME_AREA[1]-2, GAME_AREA[2]+2, GAME_AREA[3]+2]
NEXT_AREA = [ 315, 50, 114, 114 ]
MSG_ORIGIN_POS = [315, 16]  #資訊呈現座標
FONT_COLOR = color_gray

#=========================================================================================================
# 利用dictionary，將 brickID 與其對應形狀連結起來
# 定義磚塊，數字順序左上至右下
# 0,  1,  2,  3
# 4,  5,  6,  7
# 8,  9,  10, 11
# 12, 13, 14, 15
# state 0,1,2,3 處理旋轉後形狀，要旋轉時直接切換型態
brick_dict = {
    "10": ( 4, 8, 9,13), "11": ( 9,10,12,13),
    "20": ( 5, 8, 9,12), "21": ( 8, 9,13,14),
    "30": ( 8,12,13,14), "31": ( 4, 5, 8,12), "32": (8,  9, 10, 14), "33": (5,  9, 12, 13),
    "40": (10,12,13,14), "41": ( 4, 8,12,13), "42": (8,  9, 10, 12), "43": (4,  5,  9, 13),
    "50": ( 9,12,13,14), "51": ( 4, 8, 9,12), "52": (8,  9, 10, 13), "53": (5,  8,  9, 13),
    "60": ( 8, 9,12,13),
    "70": (12,13,14,15), "71": ( 1, 5, 9,13)}

# 方塊陣列(10x20) : 遊戲容器範圍, 左上角為 (0,0)
bricks_array = []
for i in range(10):
    bricks_array.append([0]*20)
# 方塊陣列(4x4)
bricks = []
for i in range(4):
    bricks.append([0]*4)
# 下一個方塊陣列(4x4)
bricks_next = []
for i in range(4):
    bricks_next.append([0]*4)
# 下一個方塊圖形陣列(4x4)
bricks_next_object = []
for i in range(4):
    bricks_next_object.append([0]*4)    
# 磚塊數量串列，紀錄方塊分布狀態，處理消去
bricks_list = []
for i in range(10):
    bricks_list.append([0]*20)

# 方塊在容器的位置. (左上角位置)
# (-2~6) : 6-(-2)+1 = 10 容器寬, 為6的時候不能旋轉方塊, 因在容器的最右方了
container_x = 3
# (-3~16) : 16-(-3)+1 = 20 容器高, -3 表示在上邊界外慢慢往下掉
container_y =-4

# 判斷遊戲結束，結束則重開一局
game_over = False

# 磚塊下降速度，方向鍵下按下時的速度
brick_down_speed = BRICK_DOWN_SPEED_MAX

# 方塊編號(1~7)
brick_id = 1
# 方塊狀態(0~3)
brick_state = 0

# 下一個磚塊編號(1~7)
brick_next_id = 1

# 分數最高紀錄
the_highest_score = 0
# 本局分數
score = 0

# 遊戲狀態
# 0:遊戲進行中
# 1:清除磚塊
# 透過不同的遊戲模式，處裡不同的工作
game_mode = 0

#-------------------------------------------------------------------------
# 函數:秀字
# 傳入:
#   text    : 字串
#   x,y    : 坐標
#   color   : 顏色
#-------------------------------------------------------------------------
def showFont( text, x, y, color):
    global canvas
    text = font.render(text, 1, color) # antialias = 1:平滑化，去鋸齒
    canvas.blit( text, (x,y))

#-------------------------------------------------------------------------
# 函數:取得磚塊索引陣列
# 傳入:
#   brickId : 方塊編號(1~7)
#   state   : 方塊狀態(0~3)
#-------------------------------------------------------------------------
def getBrickIndex( brickId, state):
    global brick_dict

    # 組合字串，方便之後資料處裡
    brickKey = str(brickId)+str(state)
    # 回傳方塊陣列
    return brick_dict[brickKey]

#-------------------------------------------------------------------------
# 轉換定義方塊到方塊陣列. 將指定的 brickId@state 填入 bricks
# 傳入:
#   brickId : 方塊編號(1~7)
#   state   : 方塊狀態(0~3)
#-------------------------------------------------------------------------
def transformToBricks( brickId, state):
    global bricks

    # 清除方塊陣列
    for x in range(4):
        for y in range(4):
            bricks[x][y] = 0
     
    # 取得磚塊索引陣列
    p_brick = getBrickIndex(brickId, state)
    
    # 將所獲資訊轉為座標
    for i in range(4):
        bx = int(p_brick[i] % 4)
        by = int(p_brick[i] / 4)
        bricks[bx][by] = brickId

#-------------------------------------------------------------------------
# 判斷是否可以複製到容器內
# 傳出:
#   true    : 可以
#   false   : 不可以
#-------------------------------------------------------------------------
def ifCopyToBricksArray():
    global bricks, bricks_array
    global container_x, container_y

    posX = 0
    posY = 0
    # container_x,y 是指4X4下墜方塊的格數座標(小容器相對於遊戲區座標原點)
    # pos 是指 container 的內部格數座標對應到的遊戲區格數座標(小容器內部方格相對於遊戲區座標原點)
    for x in range(4):
        for y in range(4):
           if (bricks[x][y] != 0):
                posX = container_x + x
                posY = container_y + y
                if (posX >= 0 and posY >= 0):
                    try:    # 使用 try_except 是省掉寫 超出 bricks_array 定義範圍的判斷程式
                        if (bricks_array[posX][posY] != 0): # 比對遊戲區（指大容器）與 container 內部每個格數座標，確保要放入的目標格位（大容器）無填色
                            return False
                    except:
                        return False
    return True

#-------------------------------------------------------------------------
# 複製方塊到容器內
#-------------------------------------------------------------------------
def copyToBricksArray():
    global bricks, bricks_array
    global container_x, container_y
    # container  是指4X4下墜方塊的格數座標
    # pos 是指 container 的內部格數座標對應到的遊戲區格數座標
    posX = 0
    posY = 0
    for x in range(4):
        for y in range(4):
            if (bricks[x][y] != 0): 
                posX = container_x + x
                posY = container_y + y
                if (posX >= 0 and posY >= 0):   #如小容器該格有東西，則填入大容器同座標位置(要先經IfCopyToBricksArray確定無衝突)
                    bricks_array[posX][posY] = bricks[x][y]
     
#-------------------------------------------------------------------------
# 初始遊戲
#-------------------------------------------------------------------------
def resetGame():
    global BRICK_DOWN_SPEED_MAX
    global bricks_array, bricks, score, the_highest_score

    # 清除磚塊陣列(容器)
    for x in range(10):
        for y in range(20):
            bricks_array[x][y] = 0
            
    # 清除方塊陣列
    for x in range(4):
        for y in range(4):
            bricks[x][y] = 0

    # 初始磚塊下降速度
    brick_down_speed = BRICK_DOWN_SPEED_MAX

    # 最高分數
    if(score > the_highest_score):
        the_highest_score = score
    # 初始分數為0
    score = 0

#---------------------------------------------------------------------------
# 判斷與設定要清除的方塊
# 傳出:
#   連線數
#---------------------------------------------------------------------------
def ifClearBrick():
    lineNum = 0
    #一行有一東西 pointNum 就+1，pointNum = 10就代表一列全有東西 => 消掉
    for y in range(20):
        pointNum = 0
        for x in range(10):
            if (bricks_array[x][y] > 0):
                pointNum = pointNum + 1
            if (pointNum == 10):
                lineNum = lineNum + 1
                for i in range(10):
                    bricks_array[i][y] = 9  # 9 : 表示應被清除
    return lineNum

#-------------------------------------------------------------------------
# 更新下一個磚塊(bricks_next), 共重繪 下一個磚塊 預呈現區
#-------------------------------------------------------------------------
def updateNextBricks(brickId):
    global bricks_next
    
    # 清除方塊陣列
    for y in range(4):
        for x in range(4):
            bricks_next[x][y] = 0

    # 取得磚塊索引陣列
    pBrick = getBrickIndex(brickId, 0)  #getBrickIndex(Id,state) => 設為初始狀態

    # 轉換方塊到方塊陣列 => 利用下列方法得到其X,Y座標
    for i in range(4):
        bx = int(pBrick[i] % 4)
        by = int(pBrick[i] / 4)
        bricks_next[bx][by] = brickId

    # 更新背景區塊
    background_bricks_next.update()

    # 更新磚塊圖
    # 此處 pos 是指 next 的，下面格子的概念轉實際繪圖
    pos_y = NEXT_AREA[1]

    for y in range(4):
        pos_x = NEXT_AREA[0]
        # bricks_next 為概念部分
        # bricks_next_object 為繪圖部分
        for x in range(4):
            if(bricks_next[x][y] != 0):
                bricks_next_object[x][y].rect[0] = pos_x
                bricks_next_object[x][y].rect[1] = pos_y
                bricks_next_object[x][y].color = tab_color[ bricks_next[x][y] ]
                bricks_next_object[x][y].update()
            pos_x = pos_x + 28        
        pos_y = pos_y + 28
                
#-------------------------------------------------------------------------
# 產生新磚塊
#-------------------------------------------------------------------------
def brickNew():
    global game_over, container_x, container_y, brick_id, brick_next_id, brick_state
    global score, game_mode

    # 判斷遊戲結束，擠爆就結束
    game_over = False
    if (container_y < 0):
        game_over = True

    # 複製方塊到容器內，使container下墜（草稿，還沒印到畫布上）
    container_y = container_y - 1
    copyToBricksArray()  #複製方塊到容器內
    
    #------------------------------------------------    
    # 判斷與設定要清除的方塊
    lines = ifClearBrick();        
    if (lines > 0):
        # 消除連線數量累加
        score =  score + lines*(1+(lines-1)*0.25)*10
        # 修改連線數量
        #modifyLabel(linesNumber, fontLinesNumber)
        # 1:清除磚塊
        game_mode = 1

    # 初始方塊位置(小容器)
    container_x = 3
    container_y =-4

    # 現在出現方塊
    brick_id = brick_next_id

    # 下個出現方塊
    # 方塊編號(1~7)
    brick_next_id = random.randint( 1, 7)
    
    # 初始方塊狀態
    brick_state = 0

    # GameOver
    if (game_over):
        # 重新開始遊戲.
        resetGame()
    
#-------------------------------------------------------------------------
# 清除的方塊
#-------------------------------------------------------------------------
def clearBrick():
    global bricks_array
    # 一列一列判斷清除方塊
    #泡沫排序法，比較 => 符合條件交換位置，把最上層不需要的消掉 => 清除還可以達到整體墜落補位的效果
    temp = 0    
    for x in range(10):
        for i in range(19): # 運送19次
            for y in range(20): 
                if (bricks_array[x][y] == 9):
                    if (y > 0):
                        temp = bricks_array[x][y - 1]   #temp 為泡沫排序法的暫存變數
                        bricks_array[x][y - 1] = bricks_array[x][y]
                        bricks_array[x][y] = temp
                        y = y - 1   # 運行直到i <= 0 也就是遊戲區最上層
            bricks_array[x][0] = 0
#-------------------------------------------------------------------------
# 初始
pygame.init()
# 顯示視窗標題
pygame.display.set_caption(u"小冠的遊戲盒")
# 建立畫布大小
canvas = pygame.display.set_mode((canvas_width, canvas_height))
# 時脈
clock = pygame.time.Clock()

# 設定字型：標楷
#font = pygame.font.SysFont('kaiu', 26)
font = pygame.font.Font('kaiu.ttf', 24) # 黑體24 
# 將繪圖方塊放入陣列
for y in range(20):
    for x in range(10):
        bricks_list[x][y] = Box(pygame, canvas, "brick_x_" + str(x) + "_y_" + str(y), [ 0, 0, 26, 26], color_gray_block)

# 將繪圖方塊放入陣列
for y in range(4):
    for x in range(4):
        bricks_next_object[x][y] = Box(pygame, canvas, "brick_next_x_" + str(x) + "_y_" + str(y), [ 0, 0, 26, 26], color_gray_block)

# 背景區塊
background = Box(pygame, canvas, "background", GAME_AREA_BORDER, color_gray)

# 背景區塊
background_bricks_next = Box(pygame, canvas, "background_bricks_next", NEXT_AREA, color_gray)

# 方塊編號(1~7)
brick_next_id = random.randint( 1, 7)
# 產生新磚塊
brickNew()

#-------------------------------------------------------------------------    
# 主迴圈
#-------------------------------------------------------------------------
running = True
time_temp = time.time()
time_now = 0    # 玩多久
while running:  # running = true 則持續跑
    # 計算時脈
    time_now = time_now + (time.time() - time_temp)
    time_temp = time.time()
    #---------------------------------------------------------------------
    # 判斷輸入
    #---------------------------------------------------------------------
    for event in pygame.event.get():
        # 離開遊戲
        if event.type == pygame.QUIT:
            running = False        
        # 判斷按下按鈕================================================================
        if event.type == pygame.KEYDOWN:
            # ESC => 退出遊戲
            if event.key == pygame.K_ESCAPE:
                running = False

            #-----------------------------------------------------------------
            # 上 => change state
            elif event.key == pygame.K_UP and game_mode == 0:
                # 在右邊界不能旋轉
                if (container_x == 8):
                    break
                # 處理特例磚塊N1、N2、I
                if (brick_id == 1 or brick_id == 2 or brick_id == 7):
                    # 長條方塊旋轉例外處理，會凸出去
                    if (brick_id == 7):
                        if (container_x < 0 or container_x == 7):
                            break
                    # 旋轉方塊，型態循環
                    brick_state = brick_state + 1
                    if (brick_state > 1):
                        brick_state = 0                    
                    # 轉換定義方塊到方塊陣列
                    transformToBricks(brick_id, brick_state)
                    # 碰到磚塊，型態-1抵銷你改變型態的動作，不讓你變
                    if (not ifCopyToBricksArray()):
                        brick_state = brick_state - 1
                        if (brick_state < 0):
                            brick_state = 1
                # 判斷磚跨L1、L2、T.                               
                elif (brick_id == 3 or brick_id == 4 or brick_id == 5):
                    # 旋轉方塊
                    brick_state = brick_state + 1
                    if (brick_state > 3):
                        brick_state = 0                    
                    # 轉換定義方塊到方塊陣列
                    transformToBricks(brick_id, brick_state)
                    # 碰到磚塊
                    if (not ifCopyToBricksArray()):
                        brick_state = brick_state - 1
                        if (brick_state < 0):
                            brick_state = 3
            #-----------------------------------------------------------------
            # 下 => 下墜加速
            elif event.key == pygame.K_DOWN and game_mode == 0:
                brick_down_speed = BRICK_DROP_PERIOD
            #-----------------------------------------------------------------
            # 左移問題，凸出遊戲區把整個小容器移回來修正
            elif event.key == pygame.K_LEFT and game_mode == 0:
                container_x = container_x - 1
                if (container_x < 0):
                    if (container_x == -1):
                        if (bricks[0][0] != 0 or bricks[0][1] != 0 or bricks[0][2] != 0 or bricks[0][3] != 0):
                            container_x = container_x + 1
                    elif (container_x == -2): 
                        if (bricks[1][0] != 0 or bricks[1][1] != 0 or bricks[1][2] != 0 or bricks[1][3] != 0):
                            container_x = container_x + 1
                    else:
                        container_x = container_x + 1
                # 碰到磚塊，移小容器修正，不讓你移
                if (not ifCopyToBricksArray()):
                    container_x = container_x + 1
            #-----------------------------------------------------------------
            # 右移問題，凸出遊戲區則把小容器移回來修正
            elif event.key == pygame.K_RIGHT and game_mode == 0:
                container_x = container_x + 1
                if (container_x > 6):
                    if (container_x == 7):
                        if (bricks[3][0] != 0 or bricks[3][1] != 0 or bricks[3][2] != 0 or bricks[3][3] != 0):
                            container_x = container_x - 1;                        
                    elif (container_x == 8):
                        if (bricks[2][0] != 0 or bricks[2][1] != 0 or bricks[2][2] != 0 or bricks[2][3] != 0):
                            container_x = container_x - 1                        
                    else:
                        container_x = container_x - 1
                # 碰到磚塊，移小容器修正，不讓你移
                if (not ifCopyToBricksArray()):
                    container_x = container_x - 1                    
        #-----------------------------------------------------------------
        # 判斷放開按鈕
        if event.type == pygame.KEYUP:
            # 按著下就保持加速狀態
            if event.key == pygame.K_DOWN:
                # 恢復正常下降速度
                brick_down_speed = BRICK_DOWN_SPEED_MAX
        
    #---------------------------------------------------------------------    
    # 清除畫面
    canvas.fill(color_block)

    # 遊戲狀態
    if (game_mode == 0):
        # 處理磚塊下降
        if(time_now >= brick_down_speed):
            container_y = container_y + 1; 
            # 碰到磚塊
            if (not ifCopyToBricksArray()): #檢查能不能移動，不行則產生新塊
                #產生新塊
                brickNew()            
            # 轉換定義方塊到方塊陣列(bricks)
            transformToBricks( brick_id, brick_state)
            # 清除時脈
            time_now = 0
    # 清除磚塊
    elif (game_mode == 1):
        clearBrick()
        # 清除完繼續玩
        game_mode = 0
        # 轉換定義方塊到方塊陣列
        transformToBricks(brick_id, brick_state)

    #---------------------------------------------------------------------    
    # 更新下一個磚塊圖形
    updateNextBricks(brick_next_id)
    # 更新繪圖
#    pos_y = 20
    pos_y = GAME_AREA[1]
    # 更新背景區塊
    background.update()
    for y in range(20):
#        pos_x = 280
        pos_x = GAME_AREA[0]
        for x in range(10):
            if(bricks_array[x][y] != 0):
                bricks_list[x][y].rect[0] = pos_x
                bricks_list[x][y].rect[1] = pos_y
                bricks_list[x][y].update()
            pos_x = pos_x + 28        
        pos_y = pos_y + 28    
    # 更新方塊
    for y in range(4):
        for x in range(4):            
            if (bricks[x][y] != 0):
                posX = container_x + x
                posY = container_y + y
                if (posX >= 0 and posY >= 0):
                    bricks_list[posX][posY].rect[0] = (posX * 28) + 5
                    bricks_list[posX][posY].rect[1] = (posY * 28) + 20
                    bricks_list[posX][posY].color = tab_color[ bricks[x][y] ]
                    bricks_list[posX][posY].update()
    #---------------------------------------------------------------------    
    # 顯示訊息
    showFont( u"下次出現方塊",MSG_ORIGIN_POS[0] , MSG_ORIGIN_POS[1], color_white)
    
    showFont( u"最高紀錄", MSG_ORIGIN_POS[0], MSG_ORIGIN_POS[1]+250, color_white)
    showFont( str(int(the_highest_score)), MSG_ORIGIN_POS[0], MSG_ORIGIN_POS[1]+280, color_white)
    #showFont( u"最大連線數", MSG_ORIGIN_POS[0], MSG_ORIGIN_POS[1]+180, color_white)
    #showFont( str(int(the_highest_score)), MSG_ORIGIN_POS[0], MSG_ORIGIN_POS[1]+210, color_white)
    showFont( u"本局分數", MSG_ORIGIN_POS[0], MSG_ORIGIN_POS[1]+180, color_white)
    showFont( str(int(score)), MSG_ORIGIN_POS[0],MSG_ORIGIN_POS[1]+210, color_white)
    #showFont( u"本局連線數", MSG_ORIGIN_POS[0], MSG_ORIGIN_POS[1]+250, color_white)
    #showFont( str(int(score)), MSG_ORIGIN_POS[0],MSG_ORIGIN_POS[1]+280, color_white)



    # 顯示FPS
    # 更新畫面
    pygame.display.update()
    clock.tick(60)

# 離開遊戲
pygame.quit()
quit() 
