
(cl:in-package :asdf)

(defsystem "rand_stu-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "Stu" :depends-on ("_package_Stu"))
    (:file "_package_Stu" :depends-on ("_package"))
  ))