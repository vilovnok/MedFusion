import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { RegisterComponent } from './register/register.component';
import { NotfoundComponent } from './notfound/notfound.component';
import { ChatComponent } from './chat/chat.component';

const routes: Routes = [
  { 
    path: '', redirectTo: '/reg', pathMatch: 'full' 
  },
  {
    path: "reg", component: RegisterComponent, title: "MedFusion"
  },
  {
    path: "agent", component: ChatComponent, title: "Agent"
  },
  // {
  //   path: "forgot-password", component: ForgotPasswordComponent, title: "Forgot password"
  // },
  // {
  //   path: "verify", component: VerifyComponent, title: "Verify"
  // },
  // {
  //   path: "home", loadChildren: () => import("./modules/main/main-route.module").then((m)=> m.MainRouteModule),
  //   canActivate:[authGuard]
  // },
  {
    path: "**", component: NotfoundComponent, title: "Not Founded"
  },
];


@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
