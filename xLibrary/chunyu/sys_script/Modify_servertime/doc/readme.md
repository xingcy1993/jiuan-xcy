新契约自动化出单工具：
API000为第一层原子脚本
API001包含第二层脚本（调用原子脚本+传参出参）、第三层脚本（组装模块--录入复核核保收费回执）



python -m robot.run -v execNo:test002 -v excel_path:D:\nodejs\xLibrary\chunyu\nb\zip\nbdata.xlsx -v env_name:预生产 -v applicationDate:2020-09-02 -d D:\nodejs\xResult\test002 nb.robot
