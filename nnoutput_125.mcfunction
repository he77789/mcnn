# generated with he77789's mcnn tool
data modify storage arr_math:in var1 set value {dec:16,num:[3,9,9,7,4,5,0,6,9,4,4,4,1,7,9],pol:-1,base:10}
data modify storage arr_math:in var2 set from storage nn_0001:nn_eval l6_0
function arr_math:call/add
data modify storage nn_0001:nn_eval l7_0 set from storage arr_math:main out
data modify storage arr_math:in var1 set value {dec:16,num:[1,3,0,3,6,0,6,3,3,1,3,4,8,4,1,9],pol:1,base:10}
data modify storage arr_math:in var2 set from storage nn_0001:nn_eval l6_1
function arr_math:call/add
data modify storage nn_0001:nn_eval l7_1 set from storage arr_math:main out
data modify storage arr_math:in var1 set value {dec:16,num:[1,6,5,5,9,6,3,9,9,4,5,6,2,6,2],pol:-1,base:10}
data modify storage arr_math:in var2 set from storage nn_0001:nn_eval l6_2
function arr_math:call/add
data modify storage nn_0001:nn_eval l7_2 set from storage arr_math:main out
data modify storage arr_math:in var1 set value {dec:16,num:[3,3,9,7,2,8,4,0,7,5,6,1,7,7,9],pol:-1,base:10}
data modify storage arr_math:in var2 set from storage nn_0001:nn_eval l6_3
function arr_math:call/add
data modify storage nn_0001:nn_eval l7_3 set from storage arr_math:main out
data modify storage arr_math:in var1 set value {dec:16,num:[8,7,1,3,9,7,1,8,2,3,4,5,3,9,0],pol:-1,base:10}
data modify storage arr_math:in var2 set from storage nn_0001:nn_eval l6_4
function arr_math:call/add
data modify storage nn_0001:nn_eval l7_4 set from storage arr_math:main out
data modify storage arr_math:in var1 set value {dec:16,num:[2,0,4,2,2,9,3,9,9,5,6,1,8,8,2,0],pol:1,base:10}
data modify storage arr_math:in var2 set from storage nn_0001:nn_eval l6_5
function arr_math:call/add
data modify storage nn_0001:nn_eval l7_5 set from storage arr_math:main out
data modify storage arr_math:in var1 set value {dec:16,num:[1,3,4,0,8,0,1,2,6,8,8,1,5,9,9],pol:-1,base:10}
data modify storage arr_math:in var2 set from storage nn_0001:nn_eval l6_6
function arr_math:call/add
data modify storage nn_0001:nn_eval l7_6 set from storage arr_math:main out
data modify storage arr_math:in var1 set value {dec:16,num:[8,7,7,5,8,9,8,8,1,4,2,0,1,3,5],pol:1,base:10}
data modify storage arr_math:in var2 set from storage nn_0001:nn_eval l6_7
function arr_math:call/add
data modify storage nn_0001:nn_eval l7_7 set from storage arr_math:main out
data modify storage arr_math:in var1 set value {dec:16,num:[2,2,1,1,5,0,6,8,1,3,7,6,4,5,7,2],pol:-1,base:10}
data modify storage arr_math:in var2 set from storage nn_0001:nn_eval l6_8
function arr_math:call/add
data modify storage nn_0001:nn_eval l7_8 set from storage arr_math:main out
data modify storage arr_math:in var1 set value {dec:16,num:[1,0,1,4,3,0,8,4,4,5,1,5,5,6,2],pol:-1,base:10}
data modify storage arr_math:in var2 set from storage nn_0001:nn_eval l6_9
function arr_math:call/add
data modify storage nn_0001:nn_eval l7_9 set from storage arr_math:main out
schedule function nn_0001:nnoutput_126 1t
say nn_0001:nnoutput_125 has finished running
