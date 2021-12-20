*** Settings ***
Library    chunyu.nb.API001
Library    Collections    


*** Test Cases ***
test
#    ${execNo}    BuiltIn.Set Variable    test001
#    ${excel_path}    BuiltIn.Set Variable    C:\\Users\\9an02\\Desktop\\nbdata.xlsx
#    ${env_name}    BuiltIn.Set Variable    预生产
#    ${applicationDate}    BuiltIn.Set Variable    2020-09-02
    #公共
#    ${dict}    chunyu.nb.API001.public    ${execNo}    ${excel_path}    ${env_name}    ${applicationDate}
    Log to Console      ${execNo}
    Log to Console      ${uid}
    Log to Console      ${execData}
    ${dict}    chunyu.nb.API001.public    ${execNo}    ${execData}
    #判断是否修改服务器时间
    chunyu.nb.API001.isModify_servertime    ${execNo}    ${dict}
    #新契约录入
    ${dict}    chunyu.nb.API001.nb_entry    ${execNo}    ${dict}
    #新契约复核
    ${dict}    chunyu.nb.API001.nb_review    ${execNo}    ${dict}
    #新契约核保
    ${dict}    chunyu.nb.API001.nb_uw    ${execNo}    ${dict}
    #新契约收费（资金收付费部分未开发）
    ${dict}    chunyu.nb.API001.nb_payment    ${execNo}    ${dict}
    #新契约回执
    ${dict}    chunyu.nb.API001.nb_receipt    ${execNo}    ${dict}
    BuiltIn.Log    ${dict}