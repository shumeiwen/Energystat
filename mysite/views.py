from django.shortcuts import render
from django.http import HttpResponse, Http404
import random
from mysite.models import Search
import numpy as np
from django.views.generic import View
from django.contrib.sessions.models import Session
import requests
from django.db import connection
import pandas as pd

mycursor=connection.cursor() #獲取資料庫連結訊息

def index(request):
    ###取出項目列表
    mycursor.execute("select * from project")
    project1=mycursor.fetchall()
    pro_col=[head[0] for head in mycursor.description]
    project=[]
    for p in project1:
        pro=dict(zip(pro_col,p))
        project.append(pro)
    
    ###取出國家別
    mycursor.execute("select * from country")
    country1=mycursor.fetchall()
    country_col=[head1[0] for head1 in mycursor.description]
    country2=pd.DataFrame(country1,columns=country_col)
    EAPS=country2[country2["Regional"]=="亞太地區"].to_dict("records")
    WAS=country2[country2["Regional"]=="亞西地區"].to_dict("records")
    EURS=country2[country2["Regional"]=="歐洲地區"].to_dict("records")
    NAS=country2[country2["Regional"]=="北美地區"].to_dict("records")
    LACS=country2[country2["Regional"]=="拉丁美洲及加勒比海地區"].to_dict("records")
    AFRS=country2[country2["Regional"]=="非洲地區"].to_dict("records")
    #print(EURS)
    
    ###計算資料選取期間
    mycursor.execute("select Max(Version) from source")
    selyear=mycursor.fetchone()
    endyear=selyear[0]
    year=np.arange(endyear-1,1999,-1)
    return render(request, 'index.html',{"project":project,"EAPS":EAPS,"WAS":WAS,"EURS":EURS,"NAS":NAS,"LACS":LACS,"AFRS":AFRS,"year":year})

def select_condition(request):
    country=list(set(request.POST.getlist("Country")))
    project=request.POST.getlist("Project")
    year=list(map(int,request.POST.getlist("year")))
    if len(country)!=0 and len(project)!=0:
        ##篩選查詢資料
        mycursor.execute("select * from RawData")
        alldata=mycursor.fetchall()
        Search_col=[head1[0] for head1 in mycursor.description]
        Search=pd.DataFrame(alldata,columns=Search_col)
        SearchData=Search[(Search["Proj_ID"].isin(project)) & (Search["Country"].isin(country)) & (Search["Year"].isin(year))]
        #print(SearchData)
        ##定義國家名稱
        mycursor.execute("select Country_id,C_Name_Cht from Country")
        CountryData=mycursor.fetchall()
        Country_col=[head1[0] for head1 in mycursor.description]
        Country_Item=pd.DataFrame(CountryData,columns=Country_col)
        CountryPair=dict(Country_Item.loc[Country_Item["Country_id"].isin(country),["Country_id","C_Name_Cht"]].to_dict("tight")["data"])

        ##定義項目名稱
        mycursor.execute("select Proj_ID,Proj_Name, ProjectName,Unit, DS_ID from project")
        ProjectData=mycursor.fetchall()
        Project_col=[head1[0] for head1 in mycursor.description]
        Project_Item=pd.DataFrame(ProjectData,columns=Project_col)
        ProjectPair=dict(Project_Item.loc[Project_Item["Proj_ID"].isin(project),["Proj_ID","ProjectName"]].to_dict("tight")["data"])


        ##置換資料及國家名稱
        SearchData=SearchData.replace({"Proj_ID":ProjectPair,"Country":CountryPair}).rename(columns={"Proj_ID":"ProjectName"})
        Project_Unit=Project_Item.loc[:,["ProjectName","Unit"]]
        SearchData=pd.merge(Project_Unit,SearchData,on="ProjectName")
        SearchData1=pd.DataFrame(columns=["ProjectName","Unit","Country"])

        for i in year:
            S=SearchData.loc[SearchData["Year"]==i,["ProjectName","Unit","Country","Data"]].rename(columns={"Data":i})
            S[i]=S[i].map(lambda x:("%.2f")%x)
            SearchData1=pd.merge(SearchData1,S, on=["ProjectName","Unit","Country"],how="outer")
        SearchData1=SearchData1.rename(columns={"ProjectName":"項目名稱","Unit":"單位","Country":"國家名稱"})
        times=len(year)
        col_num=SearchData1.shape[1]
        CountryNum=len(country)
        for j in range (1,SearchData1.shape[0]):
            if SearchData1.iloc[j,0] in list(SearchData1.iloc[0:j,0]):
                SearchData1.iloc[j,0]=""
                SearchData1.iloc[j,1]=""
            else:
                pass
        ##定義備註項內容        
        mycursor.execute("select DS_ID, Org_Name, DB_Name, Subject, Issue_Date from Source")
        SourceData=mycursor.fetchall()
        Source_col=[head1[0] for head1 in mycursor.description]   
        Source_Item=pd.DataFrame(SourceData,columns=Source_col)
        SourcePair= Project_Item.loc[Project_Item["Proj_ID"].isin(project),["Proj_Name","DS_ID"]]
        Source=pd.merge(SourcePair,Source_Item,on=["DS_ID"])
        Source['Issue_Date'] = pd.to_datetime(Source['Issue_Date'], format='%Y-%m-%d %H:%M:%S')
        Source=Source.drop_duplicates(subset=["Proj_Name"], keep="first").to_dict("records")


        return render(request,"output.html",{"output":SearchData1.to_dict("tight"),"Times":times,"Source":Source,"ColNum":col_num,"CountryNum":CountryNum})
    
    else:
        if len(country)==0 and len(project)==0:
            return render(request,"output.html", {"output":"欲查詢「項目」及「國別」皆未選取，請回上頁選取"})
        elif len(project)==0:
            return render(request,"output.html",{"output":"欲查詢「項目」未選取，請回上頁選取"})
        else:
            return render(request,"output.html",{"output":"欲查詢「國別」未選取，請回上頁選取"})
