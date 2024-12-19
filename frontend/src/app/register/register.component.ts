import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { ChatService } from '../services/chat.service';
import { NgToastService } from 'ng-angular-popup';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent {


  registerForm!: FormGroup;

  constructor(
    private fb: FormBuilder, 
    private service: ChatService,
    private toast: NgToastService,
    private router: Router) {}


  ngOnInit(): void {
    this.valid_fun();
  }

  valid_fun(): void {
    this.registerForm = this.fb.group({
      username: ['', Validators.required],
      email: ['', Validators.required],
      password: ['', Validators.required],
    });
  }

  onReg() {    
    console.log('this.registerForm.value');
    if (this.registerForm.valid) {
    //   this.service.handle_post_requests(this.registerForm.value,'auth/register').subscribe({
    //     next: (res) => {
    //       this.registerForm.reset();
    //       this.service.saveDataToLS('user_id',res.user_id);
    //       this.toast.success({detail:"SUCCESS",summary:res.message}); 
    //       this.router.navigate(['verify']);
    //     },
    //     error: (err) => {
    //       this.toast.error({detail:"ERROR",summary:err.error.detail})
    //     }});
    // } else {
    //   this.toast.error({detail:"ERROR", summary:"Зполните всю форму!", duration: 5000});
    this.router.navigate(['agent']);  
    
  }else {
    this.toast.danger('message', 'title', 5000); 
  }

    
  }

}
